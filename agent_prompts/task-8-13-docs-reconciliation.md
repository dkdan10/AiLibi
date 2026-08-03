# Agent Prompt — 8.13 Docs + scope reconciliation

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.13 — Docs + scope reconciliation, anchored to DESIGN.md (the §-rewrite is R-0, done); audits/restructure-impact-map-2026-06-04-0223.md §2f. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-docs-reconciliation`
**Depends on:** 8.12
**Section refs:** DESIGN.md (the §-rewrite is R-0, done); audits/restructure-impact-map-2026-06-04-0223.md §2f
**Complexity:** Small

Reconcile the historical build-plan prose to the post-restructure reality (accuracy, not correctness): `AGENT_IMPLEMENTATION.md` Phase-3 meeting tasks + roster prose ("5-7 agents, 1 impostor"), `README.md`, and any `AGENTS.md` §-number references that shifted. DESIGN.md itself is already rewritten (R-0).

**Files in scope:**
- AGENT_IMPLEMENTATION.md (Phase-3 meeting + roster prose → chain + 9p/2i)
- README.md (the agents/impostors/meeting one-liner)
- AGENTS.md (any DESIGN.md §-reference whose number shifted; light touch)

**Files NOT in scope:**
- DESIGN.md (R-0, already done), tasks/phase-*.md (this file aside)
- any code or committed data (all landed in 8.1–8.12)

**Definition of done:**
- [ ] `AGENT_IMPLEMENTATION.md` + `README.md` describe the accusation chain + 9p/2i + per-player tasks (no "5-7 agents / 1 impostor / 2 accusation rounds" residue); `AGENTS.md` §-references resolve.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

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
Open a PR from branch `phase-8-docs-reconciliation` with a title like `task 8.13: docs + scope reconciliation`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md (the §-rewrite is R-0, done); audits/restructure-impact-map-2026-06-04-0223.md §2f), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
