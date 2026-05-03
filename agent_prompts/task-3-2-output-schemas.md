# Agent Prompt — 3.2 Shared meeting/output schemas

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, AGENT_IMPLEMENTATION.md, and the task section in tasks/phase-3.md.

1. Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, AGENT_IMPLEMENTATION.md is the provider-neutral build plan, and the task contract below is the implementation contract for this PR.

2. Exact section reference
Implement Task 3.2 — Shared meeting/output schemas, anchored to DESIGN.md §5.3, DESIGN.md §5.5, DESIGN.md Appendix A. Do not implement work outside these references.

3. Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-output-schemas`
**Depends on:** 3.1 merged
**Section refs:** DESIGN.md §5.3, DESIGN.md §5.5, DESIGN.md Appendix A

Centralize meeting artifacts in meetings/schemas.py. Agent strategic schemas may
re-export or wrap the shared schemas, but must not duplicate independent schema
definitions.

**Files in scope:**
- meetings/schemas.py
- agents/strategic/output_schemas.py
- tests/meetings/test_schemas.py

**Files NOT in scope:**
- engine/
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `ReportDocument`, `Statement`, `VoteBallot`, `MeetingResult`, and contradiction/result DTOs match DESIGN.md §5.3 and §5.5.
- [ ] `agents/strategic/output_schemas.py` re-exports or wraps shared meeting schemas without duplicating them.
- [ ] Schemas are suitable for structured LLM output.
- [ ] No imports from engine/ under agents/.
- [ ] Relevant schema tests pass.
- [ ] `uv run mypy --strict agents meetings` passes.
- [ ] `uv run ruff check .` passes.

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
Open a PR from branch `phase-3-output-schemas` with a title like `task 3.2: shared meeting/output schemas`.
The PR description must reference DESIGN.md §5.3, DESIGN.md §5.5, DESIGN.md Appendix A, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.
