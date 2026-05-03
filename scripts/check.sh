#!/usr/bin/env bash
set -euo pipefail

uv run ruff check .
uv run ruff format --check .
uv run lint-imports
uv run python scripts/validate_task_docs.py
uv run mypy .
uv run pytest
