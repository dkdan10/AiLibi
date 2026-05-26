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
  (cd frontend && npm ci)
else
  echo "No frontend/package.json; skipping frontend dependency install."
fi
