# Codex Prompt — 3.4 Crewmate report prompt

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, CODEX_IMPLEMENTATION.md, and the task section in tasks/phase-3.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, CODEX_IMPLEMENTATION.md is the build plan, and the task contract below is the implementation contract for this PR.

2. Exact section reference
Implement Task 3.4 — Crewmate report prompt, anchored to DESIGN.md §5.3, DESIGN.md §6.6. Do not implement work outside these references.

3. Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-crewmate-report-prompt`
**Depends on:** 3.3 merged
**Section refs:** DESIGN.md §5.3, DESIGN.md §6.6

agents/strategic/prompts/crewmate_report.j2.

**Files in scope:**
- agents/strategic/prompts/crewmate_report.j2

**Files NOT in scope:**
- engine/
- agents/tactical/
- llm/ client code
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Crewmate report prompt exists and targets the shared `ReportDocument` schema.
- [ ] Prompt uses rendered memory view and public transcript inputs only.
- [ ] Prompt includes a version marker.
- [ ] No code outside the prompt file is modified.

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
Open a PR from branch `phase-3-crewmate-report-prompt` with a title like `task 3.4: crewmate report prompt`.
The PR description must reference DESIGN.md §5.3, DESIGN.md §6.6, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.
