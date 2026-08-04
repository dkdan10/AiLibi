# AGENTS.md

You are an AI coding agent working on AiLibi. Read this file before every
task, then read docs/architecture.md and the task contract in tasks/phase-N.md.

## One-time onboarding

Read once, before your first task: `AGENT_IMPLEMENTATION.md`. It is the
provider-neutral build plan and orients you on the overall multi-phase shape.
You do not need to re-read it per task — the task contract in
tasks/phase-N.md plus the prompt in agent_prompts/ is the implementation
contract for each PR.

## Source of truth

- `docs/architecture.md` is the current-architecture note and the authority on
  the system's layering as built — packages, the enforced boundaries, the
  determinism and substrate-ladder contracts. Read it before touching a package
  boundary.
- `DESIGN.md` is the **historical design record**: a v0.1 draft, reconciled to
  HEAD as of the Phase 6 close (2026-05-30). Read it for design rationale and
  the history of a decision, not for current architecture. Where the two
  disagree, `docs/architecture.md` wins.
- Every task references specific sections — of its own contract and of the
  documents that contract names. If the section says X, you do X — even if you
  think Y is better. If you genuinely think the design is wrong, leave a comment
  in the PR description and stop. Do not change the design unilaterally.
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

- Python 3.11. Type hints on every function. `mypy --strict` is enforced
  repo-wide (pyproject sets `strict = true`; `check.sh` runs `mypy .`).
- Pydantic v2 for all data classes that cross module boundaries. Frozen
  dataclasses for engine state.
- `asyncio` for concurrent agent dispatch. No threads.
- `ruff` and `ruff format` must pass.
- Tests are `pytest`. Property tests use `hypothesis`.

## Graduation sweeps (substrate levers)

When a substrate lever graduates — its `AILIBI_*` env gate retired, its
behavior unconditional, normally at a baseline adopting record — the graduating
PR must ALSO sweep the prose. Grep the lever's snake_case name repo-wide and
rewrite every docstring, comment, and doc line that still describes it as live
or default-OFF: the lever stays in the substrate stamp for provenance, but
nothing may still tell a reader it can be switched off. Stale "default-OFF"
prose is exactly the drift class the Task-19.2 in-code sweep had to clean;
sweeping at graduation is the structural fix that stops it regenerating. The
registry in `orchestrator/replay.py` (`_RETIRED_ALWAYS_ON_LEVERS` /
`_TOGGLEABLE_LEVER_RESOLVERS`) is the source of truth for which levers are
still live.

## Environment setup

- In a fresh local, container, or agent runner environment, run
  `bash scripts/setup_env.sh` before testing or implementation work.
- For final verification, run `bash scripts/check.sh`. Targeted `uv run ...`
  commands are fine while developing, but the shared check script is the
  required full-project gate.
- New Python dependencies must be added intentionally with `uv add ...` or
  `uv lock`. Commit both `pyproject.toml` and `uv.lock` when dependencies
  change.
- **Shallow clones.** Hosted CI and agent-runner environments often provide a
  shallow clone (the Phase-19 input audit's session saw ~50 commits until it
  unshallowed). Any history-derived claim — merged-PR counts, `git log --follow`
  provenance — requires `git fetch --unshallow` (or an equivalent full fetch)
  first. Never read a truncated log as the project's history.
- **LLM providers.** CI and `bash scripts/check.sh` always run against the
  deterministic fake provider and never hit the network. Four providers sit
  behind the `LLMClient` Protocol — the fake plus three real ones — selected by
  `AILIBI_LLM_PROVIDER`: Anthropic (`anthropic`, needs `ANTHROPIC_API_KEY`);
  a local **Ollama** open model (`ollama`, `qwen3.5:9b` on `localhost:11434`,
  run with thinking disabled, free); and hosted **Featherless**
  (`featherless`, `Qwen/Qwen3.6-27B`, OpenAI-compatible, needs
  `FEATHERLESS_API_KEY`, recorded as $0 on a flat-rate subscription) — the
  **canonical eval provider** since Phase 14, its model locked 2026-07-12 at
  Task 16.2 (audits/audit-phase-16-model-lock.md) and pinned non-thinking. The
  committed sample sets under `replays/samples/` are the **baseline-6** record
  (the Task-18.12 meeting-layer adopting record), recorded on that locked
  model; each set's `MANIFEST.md` is the canonical provenance record.
  No real provider is reached in CI: the live integration tests are opt-in
  behind env gates — `AILIBI_RUN_REAL_PROVIDER_TESTS=1` covers the Anthropic
  tests AND the live Featherless smoke tests (which additionally need
  `FEATHERLESS_API_KEY`; `tests/llm/test_real_provider.py`), and
  `AILIBI_RUN_OLLAMA_TESTS=1` the local Ollama round-trip. The Featherless
  client's CI coverage is unit tests against a mock transport (no network).

## Definition of done (always)

A task is not done until:
- All checkboxes in the task's "Definition of done" are checked.
- `bash scripts/check.sh` passes locally.
- The diff touches only the files listed as in scope.
- The PR description references the section(s) the task contract names
  (DESIGN.md sections where the contract cites them; `docs/architecture.md`
  for layering).

## GitHub operations

GitHub tooling is environment-dependent: different dispatch environments
provision different integrations, so make no absolute assumption that one
path always works or another always fails. Detect what is available and use
it — do not declare GitHub work impossible without trying both.

- **Prefer whatever is actually configured.** If the `gh` CLI is present
  and authenticated (`which gh && gh auth status`), use it for GitHub work
  — PRs, issues, comments, diffs, reviews. If `gh` is absent or
  unauthenticated, use the environment's GitHub integration instead (e.g.
  the MCP-based `github` tools, `mcp__github__*`), which is the working
  path in environments where `gh` is not provisioned. Fall back from one to
  the other rather than giving up.
- **For PR creation,** populate every section of
  `.github/pull_request_template.md` (see "PR description (always)" below).
  On the `gh` path use the `gh pr create --body "$(cat <<EOF ... EOF)"`
  pattern; on the integration-tool path pass the same populated body to the
  create-PR call. Either way the body must contain every required section —
  never ship an empty body.

## PR description (always)

Every PR — task-driven or ad-hoc (audits, hygiene, hotfixes) — must
populate the sections in `.github/pull_request_template.md`:

- `## Summary` — 1–3 bullets stating what changed and why.
- `## Definition of done` — copy the task's checklist and tick each item;
  for ad-hoc PRs, list the scope you actually executed.
- `## Decisions` — every judgment call resolved without human input.
  Write "None." if there were none.
- `## Questions` — blocking questions only; omit the section if none.

When creating the PR, pass the fully populated template as the body: on the
`gh` path, `gh pr create --body` with a here-doc containing it; on the
integration-tool path, the body parameter of the create-PR call. An
explicit body overrides the repo template, so the body you pass must itself
include every required section. Auto-fill or empty-body shortcuts (e.g.
`gh pr create --fill` / `--body ""`, or omitting the body field) ship empty
bodies and are not permitted.

## When you're stuck

Don't guess. In the PR description, write a "Questions" section listing what
you need clarified. Stop and open the PR; the human will respond.
