#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required to set up AiLibi dependencies." >&2
  echo "Install uv first, then run: bash scripts/setup_env.sh" >&2
  exit 1
fi

# Mirrors scripts/check.sh: AILIBI_SKIP_FRONTEND=1 skips the frontend
# dependency install below. CI's Python job sets it because the dedicated
# frontend-checks job installs and builds the frontend itself; installing it
# here too is pure duplicate work. Validated loudly — an unrecognised value is a
# typo, not an "install it anyway".
skip_frontend="${AILIBI_SKIP_FRONTEND:-0}"
if [ "$skip_frontend" != "0" ] && [ "$skip_frontend" != "1" ]; then
  echo "AILIBI_SKIP_FRONTEND must be 0 or 1 (got '$skip_frontend')." >&2
  exit 1
fi

# `--group dev` names the gate toolchain (pytest, hypothesis, ruff, mypy +
# stubs, import-linter) explicitly. uv includes the `dev` group by default, so
# this is not a behaviour change — it is the declaration that the environment
# this script builds is the DEV environment, now that the runtime dependency set
# in pyproject.toml no longer carries those tools. The version probes below fail
# loudly if the group ever stops being installed.
uv sync --locked --group dev

uv run python --version
uv run ruff --version
uv run mypy --version
uv run pytest --version
uv run lint-imports --version

# Frontend dependencies (Phase 4.3+). Skipped with AILIBI_SKIP_FRONTEND=1 and on
# branches without frontend/. When the frontend IS present and not opted out, npm
# is a hard prerequisite: failing loudly here beats a partially-configured
# environment that breaks later in obscure ways. Uses `npm ci` for a reproducible
# install from the committed lockfile (fails on package.json/lock drift rather
# than silently rewriting the lock).
if [ "$skip_frontend" = "1" ]; then
  echo "Skipping frontend dependency install (AILIBI_SKIP_FRONTEND=1)."
elif [ -f frontend/package.json ]; then
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
