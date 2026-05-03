# Codex Prompt — 4.7 BeliefMatrix

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, CODEX_IMPLEMENTATION.md, and the task section in tasks/phase-4.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, CODEX_IMPLEMENTATION.md is the build plan, and the task contract below is the implementation contract for this PR.

2. Exact section reference
Implement Task 4.7 — BeliefMatrix, anchored to DESIGN.md §6, DESIGN.md §7. Do not implement work outside these references.

3. Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-beliefmatrix`
**Depends on:** 4.3 merged
**Section refs:** DESIGN.md §6, DESIGN.md §7

Heatmap of who suspects whom.

**Files in scope:**
- frontend/src/components/BeliefMatrix.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/src/store/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] BeliefMatrix renders a heatmap of suspicion/trust relationships from sanitized spectator DTOs.
- [ ] Component consumes the shared store/API shape from 4.3.
- [ ] Frontend build/check command passes if configured.

4. Pre-flight checklist
- Read AGENTS.md, DESIGN.md, CODEX_IMPLEMENTATION.md, and the task section before editing.
- Inspect the current implementation before editing.
- Confirm the dependency listed in the task contract is present in the current branch.
- Identify the existing local patterns for the files in scope and follow them.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
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
Open a PR from branch `phase-4-beliefmatrix` with a title like `task 4.7: beliefmatrix`.
The PR description must reference DESIGN.md §6, DESIGN.md §7, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.
