#!/usr/bin/env bash
set -euo pipefail

# AILIBI_SKIP_FRONTEND=1 drops the frontend leg below. CI's Python job sets it
# because the dedicated frontend-checks job already runs the same
# tsc:check + build in parallel — without the opt-out the frontend is built
# twice per run. Unset locally, so this script stays the one-command truth.
# Validated loudly: an unrecognised value is a typo, not a "run it anyway".
skip_frontend="${AILIBI_SKIP_FRONTEND:-0}"
if [ "$skip_frontend" != "0" ] && [ "$skip_frontend" != "1" ]; then
  echo "AILIBI_SKIP_FRONTEND must be 0 or 1 (got '$skip_frontend')." >&2
  exit 1
fi

uv run ruff check .
uv run ruff format --check .
uv run lint-imports
uv run python scripts/validate_task_docs.py
uv run python scripts/generate_prompts.py --check
uv run mypy .
uv run pytest

# Frontend checks (Phase 4.3+). Run after the Python gates (Python is the
# source of truth; the frontend is downstream). Skipped with a warning when
# AILIBI_SKIP_FRONTEND=1 (see above) or when frontend/ is absent, so branches
# without 4.3 still pass. When the frontend IS present and not opted out, npm is
# required: fail with an explicit message rather than a cryptic
# command-not-found so the gate behaves deterministically across environments.
if [ "$skip_frontend" = "1" ]; then
  echo "Skipping frontend checks (AILIBI_SKIP_FRONTEND=1)." >&2
elif [ -f frontend/package.json ]; then
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
