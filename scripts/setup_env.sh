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
