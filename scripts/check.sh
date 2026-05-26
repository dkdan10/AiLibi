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
# frontend/ is absent, so branches without 4.3 still pass.
if [ -f frontend/package.json ]; then
  echo "Running frontend checks..."
  (cd frontend && npm run tsc:check && npm run build)
else
  echo "Skipping frontend checks (frontend/package.json not present)." >&2
fi
