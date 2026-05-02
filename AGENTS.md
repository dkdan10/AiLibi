# AGENTS.md

You are an AI coding agent (Codex) working on AiLibi. Read this file before
every task, then read DESIGN.md and CODEX_IMPLEMENTATION.md as referenced.

## Source of truth

- `DESIGN.md` is the authoritative architecture document. Every task references
  a specific section. If the section says X, you do X — even if you think Y
  is better. If you genuinely think the design is wrong, leave a comment in
  the PR description and stop. Do not change the design unilaterally.
- `CODEX_IMPLEMENTATION.md` is the build plan. The current task description
  in the prompt overrides it where they conflict.

## Three load-bearing rules (DESIGN.md §0)

1. **Tick-based deterministic engine.** Engine is a pure function of state
   and actions. Replays must be byte-identical from a seed.
2. **Two-tier agent reasoning.** LLMs only at meetings or specific triggers.
   Tactical decisions are rule-based. Do not put LLM calls inside `agents/tactical/`.
3. **Structured memory first.** Agents reason from a typed event log and a
   derived belief state. The LLM sees a *rendered* memory view, not raw chat.

## Architectural constraints

- **The observation firewall is non-negotiable.** `agents/` MUST NOT import
  from `engine/`. This is enforced by `import-linter` in CI. If your task
  needs an engine type in agent code, it is the wrong task — stop and ask.
- **No global state.** No singletons, no module-level mutable state. All state
  is owned by an explicit object and passed through.
- **No silent fallbacks.** If something is invalid, raise. Do not paper over.

## Coding conventions

- Python 3.11. Type hints on every function. `mypy --strict` must pass on
  `engine/`, `observation/`, `agents/`.
- Pydantic v2 for all data classes that cross module boundaries. Frozen
  dataclasses for engine state.
- `asyncio` for concurrent agent dispatch. No threads.
- `ruff` and `ruff format` must pass.
- Tests are `pytest`. Property tests use `hypothesis`.

## Environment setup

- In a fresh local, container, or Codex Web environment, run
  `bash scripts/setup_env.sh` before testing or implementation work.
- For final verification, run `bash scripts/check.sh`. Targeted `uv run ...`
  commands are fine while developing, but the shared check script is the
  required full-project gate.
- New Python dependencies must be added intentionally with `uv add ...` or
  `uv lock`. Commit both `pyproject.toml` and `uv.lock` when dependencies
  change.

## Definition of done (always)

A task is not done until:
- All checkboxes in the task's "Definition of done" are checked.
- `bash scripts/check.sh` passes locally.
- The diff touches only the files listed as in scope.
- The PR description references the DESIGN.md section(s) implemented.

## When you're stuck

Don't guess. In the PR description, write a "Questions" section listing what
you need clarified. Stop and open the PR; the human will respond.
