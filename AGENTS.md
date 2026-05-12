# AGENTS.md

You are an AI coding agent working on AiLibi. Read this file before every
task, then read DESIGN.md and the task contract in tasks/phase-N.md.

## One-time onboarding

Read once, before your first task: `AGENT_IMPLEMENTATION.md`. It is the
provider-neutral build plan and orients you on the overall multi-phase shape.
You do not need to re-read it per task — the task contract in
tasks/phase-N.md plus the prompt in agent_prompts/ is the implementation
contract for each PR.

## Source of truth

- `DESIGN.md` is the authoritative architecture document. Every task references
  a specific section. If the section says X, you do X — even if you think Y
  is better. If you genuinely think the design is wrong, leave a comment in
  the PR description and stop. Do not change the design unilaterally.
- `tasks/phase-N.md` is the task contract — branch, dependencies, files in/out
  of scope, definition of done, implementation hint, public types introduced.
  The matching `agent_prompts/task-*.md` is generated from this contract by
  `scripts/generate_prompts.py`. Do not hand-edit prompts; edit
  `tasks/phase-N.md` and regenerate.

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

- In a fresh local, container, or agent runner environment, run
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

## PR description (always)

Every PR — task-driven or ad-hoc (audits, hygiene, hotfixes) — must
populate the sections in `.github/pull_request_template.md`:

- `## Summary` — 1–3 bullets stating what changed and why.
- `## Definition of done` — copy the task's checklist and tick each item;
  for ad-hoc PRs, list the scope you actually executed.
- `## Decisions` — every judgment call resolved without human input.
  Write "None." if there were none.
- `## Questions` — blocking questions only; omit the section if none.

When creating the PR with `gh pr create`, pass `--body` with a here-doc
containing the populated template. Passing `--body` overrides the
template, so the here-doc itself must include every required section.
`gh pr create --fill` and `gh pr create --body ""` both ship empty bodies
and are not permitted.

## When you're stuck

Don't guess. In the PR description, write a "Questions" section listing what
you need clarified. Stop and open the PR; the human will respond.
