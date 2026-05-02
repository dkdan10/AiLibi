#!/usr/bin/env bash
set -euo pipefail

uv run ruff check .
uv run lint-imports
uv run mypy --strict engine observation agents
uv run pytest
