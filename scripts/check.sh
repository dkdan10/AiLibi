#!/usr/bin/env bash
set -euo pipefail

uv run ruff check .
uv run ruff format --check .
uv run lint-imports
uv run python scripts/validate_task_docs.py
uv run python scripts/generate_prompts.py --check
uv run mypy .
uv run pytest

# Frontend checks (Phase 4.3+). Run after the Python gates (Python is the
# source of truth; the frontend is downstream). Skipped with a warning when
# frontend/ is absent, so branches without 4.3 still pass. When the frontend IS
# present, npm is required: fail with an explicit message rather than a cryptic
# command-not-found so the gate behaves deterministically across environments.
if [ -f frontend/package.json ]; then
  if ! command -v npm >/dev/null 2>&1; then
    echo "npm is required to run frontend checks (frontend/package.json present)." >&2
    echo "Install Node.js/npm, or run scripts/check.sh on a host with npm." >&2
    exit 1
  fi
  echo "Running frontend checks..."
  (cd frontend && npm run tsc:check && npm run build)
else
  echo "Skipping frontend checks (frontend/package.json not present)." >&2
fi
