# Agent Prompt — 1.B2 Leak test implementation

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-1.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 1.B2 — Leak test implementation, anchored to DESIGN.md §11.2, DESIGN.md §1.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-1.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-1-leak-test-implementation`
**Depends on:** 1.7 merged
**Section refs:** DESIGN.md §11.2, DESIGN.md §1.3
**Complexity:** Small

Once ObservationPacket exists, implement the actual leak-test assertions. Can be done in parallel with task 1.8.

**Files in scope:**
- eval/leak_test.py

**Files NOT in scope:**
- engine/
- agents/
- api/
- frontend/
- llm/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] eval/leak_test.py asserts observation purity for hidden fields.
- [ ] Leak test runs against three scripted games.
- [ ] pytest eval/leak_test.py passes.
- [ ] No engine code is modified.
- [ ] ruff check . passes.

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
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
Open a PR from branch `phase-1-leak-test-implementation` with a title like `task 1.B2: leak test implementation`.
The PR description must reference DESIGN.md §11.2, DESIGN.md §1.3, list the definition-of-done checklist, and include `Decisions` and (if blocking) `Questions` sections.
