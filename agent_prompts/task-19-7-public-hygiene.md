# Agent Prompt — 19.7 Public and build hygiene + the MIT posture

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.7 — Public and build hygiene + the MIT posture, anchored to audits/audit-phase-19-triage.md §7 item 8 [S-Codex/S-Claude; §8 rows 12, 16] + locked decision 4 (MIT + minimal); .github/workflows/ci.yml (no `permissions:` block; checkout@v6/setup-python@v6/setup-uv@v7/setup-node@v4 by tag; the frontend-checks job :32-57 repeating scripts/check.sh:17-24); pyproject.toml:7-21 (pytest/ruff/mypy/hypothesis/import-linter in RUNTIME deps) vs :48-51 (dev group = one stub); package-lock.json (a 10-line dead root lockfile); the absent LICENSE/CONTRIBUTING/SECURITY (verified absent at HEAD). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-public-hygiene`
**Depends on:** 19.6
**Section refs:** audits/audit-phase-19-triage.md §7 item 8 [S-Codex/S-Claude; §8 rows 12, 16] + locked decision 4 (MIT + minimal); .github/workflows/ci.yml (no `permissions:` block; checkout@v6/setup-python@v6/setup-uv@v7/setup-node@v4 by tag; the frontend-checks job :32-57 repeating scripts/check.sh:17-24); pyproject.toml:7-21 (pytest/ruff/mypy/hypothesis/import-linter in RUNTIME deps) vs :48-51 (dev group = one stub); package-lock.json (a 10-line dead root lockfile); the absent LICENSE/CONTRIBUTING/SECURITY (verified absent at HEAD)
**Complexity:** Medium

Public-repo basics plus CI hygiene in one pass. CI: add `permissions: contents: read`,
pin every action to a full SHA (tag in a comment), and deduplicate the frontend build —
`scripts/check.sh` keeps its leg (one-command local truth) and CI keeps ONE frontend
build, not two paths building the same thing per run. Packaging: partition dev tools
(pytest, ruff, mypy, hypothesis, import-linter) into the dev group, keep runtime deps
minimal, regenerate the lock, and make CI/setup install the dev group; delete the dead
root `package-lock.json`. Known, accepted boundary: `eval/leak_test.py` imports pytest at
module level and `training.bakeoff.harness` imports from it, so training/eval remain
dev-environment surfaces until 19.24 promotes the scanners to a pytest-free library — the
runtime-only claim below covers the production packages ONLY, and the contract says so
rather than hiding it. Posture (locked decision 4): LICENSE (MIT), a short
CONTRIBUTING.md (agent-built experiment; the contract workflow; issues welcome, PRs are
not the workflow), and SECURITY.md (the replay API is an intentionally unauthenticated GM
view — loopback only; how to report).

**Files in scope:**
- .github/workflows/ci.yml
- scripts/check.sh
- scripts/setup_env.sh; (the dev-group install, if the partition requires it)
- pyproject.toml
- uv.lock
- package-lock.json; (deleted)
- LICENSE (new)
- CONTRIBUTING.md (new)
- SECURITY.md (new)

**Files NOT in scope:**
- frontend/package.json (19.12's file)
- README.md (19.1's file — link additions ride the README chain)

**Definition of done:**
- [ ] CI runs green with the permissions block, SHA-pinned actions, and exactly one frontend build per run.
- [ ] `uv run pytest` and `bash scripts/check.sh` still pass locally after the dependency partition (dev group installed by setup), and the runtime-only smoke actually proves the partition: `uv run --no-dev --exact python -c "import api.main, orchestrator.game, meetings.manager, agents.strategic.prompts.loader, llm.provider, engine.tick"` — the flags are load-bearing (a bare `uv run` re-syncs the dev group and vacuously passes) and the ENTRY-MODULE list is load-bearing too (the six package `__init__`s are all 0 bytes, so importing bare packages executes none of the production graph) — plus an assertion that pytest/mypy are absent from that environment. training/eval are explicitly excluded from the claim until 19.24 (the known `eval.leak_test` pytest import, stated in the partition's notes).
- [ ] LICENSE is MIT with the owner's copyright line; CONTRIBUTING and SECURITY match locked decision 4's posture and the deployment doc's trust boundary.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Read `.github/workflows/ci.yml` first to see which job runs what: the duplication is the
frontend-checks job re-running the `npm ci && tsc:check && build` that check.sh's leg also
runs inside the Python job. Keep the split that maximizes CI parallelism and delete the
other copy. For the partition, `uv`'s dependency groups + `uv sync --group dev` is the
shape; CI must install the group explicitly.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-19-public-hygiene` with a title like `task 19.7: public and build hygiene + the mit posture`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 8 [S-Codex/S-Claude; §8 rows 12, 16] + locked decision 4 (MIT + minimal); .github/workflows/ci.yml (no `permissions:` block; checkout@v6/setup-python@v6/setup-uv@v7/setup-node@v4 by tag; the frontend-checks job :32-57 repeating scripts/check.sh:17-24); pyproject.toml:7-21 (pytest/ruff/mypy/hypothesis/import-linter in RUNTIME deps) vs :48-51 (dev group = one stub); package-lock.json (a 10-line dead root lockfile); the absent LICENSE/CONTRIBUTING/SECURITY (verified absent at HEAD)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
