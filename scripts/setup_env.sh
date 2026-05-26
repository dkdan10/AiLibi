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

# Frontend dependencies (Phase 4.3+). Skipped gracefully on branches that do
# not include frontend/ yet, or in environments without npm. Idempotent:
# re-running just re-resolves against the committed package-lock.json.
if [ -f frontend/package.json ]; then
  if command -v npm >/dev/null 2>&1; then
    echo "Installing frontend dependencies (npm install in frontend/)..."
    (cd frontend && npm install)
  else
    echo "npm not found; skipping frontend dependency install." >&2
  fi
else
  echo "No frontend/package.json; skipping frontend dependency install."
fi
