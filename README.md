# AiLibi

AiLibi is a deterministic multi-agent social-deduction simulation testbed. The
current codebase contains the Phase 0/1 foundation: engine state, rules,
visibility, observation packets, audit logs, replay hashes, and project gates.

## Setup

```bash
bash scripts/setup_env.sh
```

Run the full local gate before opening a PR:

```bash
bash scripts/check.sh
```

The check script runs ruff, ruff format check, import-linter, task/prompt
validation, mypy, and pytest.

## API Baseline

The Phase 0 API baseline exposes a health endpoint:

```bash
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Or with Docker Compose:

```bash
docker compose up api
```

Then visit `http://localhost:8000/health`.

## Architecture Notes

- `engine/` owns hidden game truth and deterministic state transitions.
- `observation/` is the information firewall that produces agent-visible
  packets and audit logs.
- `agents/` must not import from `engine/`; CI enforces this with import-linter.
- `orchestrator/` is the intended boundary layer for translating future
  agent intents into engine actions and recording replay artifacts.

## Current Limitations

Agents, tactical policies, meetings, LLM integration, the spectator frontend,
and tournament dashboards are future phases. The current API is intentionally
minimal and exists to satisfy the Phase 0 boot path.
