# AGENTS.md

You are an AI coding agent working on AiLibi. Read this file before every
task, then read docs/architecture.md and the assigned task card.

## Work routing

New work uses one canonical card at `tasks/work/<slug>.md`. Read
[docs/workflow.md](docs/workflow.md) when starting work with this format;
[tasks/README.md](tasks/README.md) names the current outcome and next candidates.
Cards are dispatched by path and have no generated prompt copies.

`tasks/phase-*.md` and `agent_prompts/` remain historical contracts and their
generated exports. Their existing validators still run. When explicitly
resuming a phase task, follow that contract, including its exact file scope;
edit its source and regenerate rather than hand-editing its prompt.
`AGENT_IMPLEMENTATION.md` is optional historical onboarding, not required
reading for new cards.

## Source of truth

- `docs/architecture.md` is the current-architecture note and the authority on
  the system's layering as built — packages, the enforced boundaries, the
  determinism and substrate-ladder contracts. Read it before touching a package
  boundary.
- `DESIGN.md` is the **historical design record**: a v0.1 draft, reconciled to
  HEAD as of the Phase 6 close (2026-05-30). Read it for design rationale and
  the history of a decision, not for current architecture. Where the two
  disagree, `docs/architecture.md` wins.
- The assigned card defines the problem, acceptance evidence, permitted scope,
  and record impact. Its referenced architecture and decision sections bind.
  Inspect the current implementation before choosing a solution. If meeting
  the goal requires changing a protected decision that the owner has not
  already authorized, describe the concrete choice and ask; do not change the
  design unilaterally.
- `docs/workflow.md` defines the prospective task lifecycle. It does not amend
  historical task contracts, recorded experiment verdicts, or baseline evidence.

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
behavior unconditional, normally at a baseline adopting record — **delete the
mechanism, keep the stamp key and one history line.** What goes: the
`*_enabled()` resolver, the `ENV_*` constant and its `__all__` entry, the `env`
parameter wherever no live resolver is reachable from that call chain, every
`if <lever>_enabled():` guard (replaced by its always-taken side), and the tests
that pin the parameter rather than the behavior. What stays: the lever's
snake_case key in `orchestrator/replay.py::_RETIRED_ALWAYS_ON_LEVERS`, so a
recording keeps self-describing its substrate and the loader can still refuse a
legacy stamp recording it OFF — plus at most one trailing provenance line naming
the adopting record.

The prose sweep is still required; it is the smaller half. Grep the lever's
snake_case name repo-wide and rewrite every docstring, comment, and doc line
that still describes it as live or default-OFF: nothing may tell a reader it can
be switched off. The registry in `orchestrator/replay.py`
(`_RETIRED_ALWAYS_ON_LEVERS` / `_TOGGLEABLE_LEVER_RESOLVERS`) is the source of
truth for which levers are still live.

Keeping the shape is how nine dead resolvers accumulated across five
graduations. Task 20.37 is the precedent for doing it properly: it swept both
generations at once (seventeen resolvers, 332 source lines, 227 test env-lines)
and left behind the structural gate that stops them regenerating —
`tests/meetings/test_lever_registry.py` walks `agents/`, `meetings/` and
`orchestrator/` with `ast` and fails on any `*_enabled` function that neither
reads its `env` argument nor returns anything but a bare `True`.

## Craft rules (added at the Phase-20 planning PR)

These rules bind new cards and phase tasks alike. Historical task prompts also
repeat them.

1. **Lead with intent, not history.** A docstring or comment states what the
   code does and why, now. Provenance (task ids, audit paths, PR numbers) is at
   most one trailing line. Source files are not changelogs — the review counted
   2,691 lines of pure history narration in non-test Python.
2. **A gate must be able to fail.** Every new test or check that guards an
   invariant ships with a planted or perturbed case proving it bites, and it
   checks the semantics it claims (entitlement, not just shape). A gate nobody
   can fail is prose.
3. **Retire means delete.** When a lever graduates or a branch dies, delete the
   mechanism. "Graduation sweeps" above states the rule in full and names its
   precedent; this applies to every dead branch, not only substrate levers.
4. **No internal dialect on user-facing surfaces.** UI copy, rendered game
   prompts, spoken `free_text`, README and docs carry no task/audit ids, no
   threshold arithmetic, and no undefined jargon; a term that must survive is
   defined in `docs/glossary.md`.
5. **Claims are verifiable-shaped.** A documentation claim names the mechanism
   that enforces it ("never breached in CI: import-linter contract +
   planted-leak test + recursive leak sweep"), never a bare superlative; a
   number is recomputed from committed bytes and the command goes in the PR.
6. **Blast radius before scope.** Grep every consumer of a symbol, path, or
   constant before changing it. For a new card, expected files may include
   directly necessary call-site, test, generated-output, and documentation
   updates within its permitted boundaries; record this follow-through in the
   PR. Changes to protected architecture, behavior beyond the card, public
   compatibility, dependencies, or spending need an owner decision unless
   already authorized. A phase task keeps its exact file scope: stop and ask
   before widening it.
7. **Every behaviour change carries its record impact.** New cards state
   `## Record impact` (none / lever-gated until the adopting record / the
   record itself / post-record) and `## Validation` (commands that prove
   acceptance). Phase contracts retain `**Record impact:**` and
   `**Measurement:**`. Anything that changes rendered prompt bytes or detector output is
   lever-gated default-OFF until its adopting record, and graduates under rule 3.

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
- **LLM providers.** CI and `bash scripts/check.sh` use the deterministic fake
  provider; real-provider integration tests remain opt-in. Read
  [llm/README.md](llm/README.md) and [.env.example](.env.example) for provider,
  prompt-family, model, and test-gate configuration. Read each recording set's
  `MANIFEST.md` for its actual provenance and `docs/architecture.md` for the
  current baseline routing. A live run needs an authorized provider and run
  budget, including token and wall-time limits even on a flat-rate subscription.

## Definition of done (always)

A task is not done until:
- All checkboxes in the card's "Acceptance" or phase task's "Definition of
  done" are checked, with evidence for each claim.
- `bash scripts/check.sh` passes locally.
- The diff satisfies the assigned scope: a new card's permitted boundaries and
  documented mechanical follow-through, or a phase task's exact file list.
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
  On the `gh` path write the body to a file and use `gh pr create --body-file`;
  on the integration-tool path pass the same populated body to the
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
`gh` path, `gh pr create --body-file` with the prepared file; on the
integration-tool path, the body parameter of the create-PR call. An
explicit body overrides the repo template, so the body you pass must itself
include every required section. Auto-fill or empty-body shortcuts (e.g.
`gh pr create --fill` / `--body ""`, or omitting the body field) ship empty
bodies and are not permitted.

## When you're stuck

Resolve routine implementation choices within the authorized scope and record
material decisions in the PR. If a missing decision blocks the task, explain
the concrete choice under "Questions" in a draft PR and ask the owner. Continue
independent authorized work while awaiting that answer; do not claim completion
with acceptance evidence missing.
