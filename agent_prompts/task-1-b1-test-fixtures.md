# Agent Prompt — 1.B1 Test fixtures

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, AGENT_IMPLEMENTATION.md, and the task section in tasks/phase-1.md.

1. Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, AGENT_IMPLEMENTATION.md is the provider-neutral build plan, and the task contract below is the implementation contract for this PR.

2. Exact section reference
Implement Task 1.B1 — Test fixtures, anchored to DESIGN.md §11.1. Do not implement work outside these references.

3. Task contract
The authoritative task contract is copied below from tasks/phase-1.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-1-test-fixtures`
**Depends on:** 1.3 merged
**Section refs:** DESIGN.md §11.1

Hand-author tests/fixtures/scripted_game_*.json short canned games used by the determinism test. Does not touch engine code.

**Files in scope:**
- tests/fixtures/scripted_game_*.json

**Files NOT in scope:**
- engine/
- agents/
- observation/
- api/
- frontend/
- llm/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Short canned scripted game fixtures exist for determinism testing.
- [ ] Fixtures use the stable action schema from task 1.3.
- [ ] No engine code is modified.
- [ ] pytest fixture-loading tests pass if present.
- [ ] ruff check . passes.

4. Pre-flight checklist
- Read AGENTS.md, DESIGN.md, AGENT_IMPLEMENTATION.md, and the task section before editing.
- Inspect the current implementation before editing.
- Confirm the dependency listed in the task contract is present in the current branch.
- Identify the existing local patterns for the files in scope and follow them.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.
If something is ambiguous, stop and add a Questions section in the PR description rather than guessing.

6. Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

7. Output expectation
Open a PR from branch `phase-1-test-fixtures` with a title like `task 1.B1: test fixtures`.
The PR description must reference DESIGN.md §11.1, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.
