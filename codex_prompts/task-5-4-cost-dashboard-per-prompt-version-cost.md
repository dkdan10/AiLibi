# Codex Prompt — 5.4 Cost dashboard (per-prompt-version cost)

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §11.3. Do not implement work outside these references.

3. Files in scope
You may edit only:
- eval/TODO_REVIEW cost dashboard metric file

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] Per-prompt-version cost metric/dashboard data is implemented.
- [ ] Cost data is included in tournament JSON report.
- [ ] Relevant eval tests pass.
- [ ] ruff check . passes.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Files explicitly NOT in scope:
- engine/
- agents/
- llm/ provider behavior
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-5-cost-dashboard` with a title like `task 5.4: cost dashboard (per-prompt-version cost)`.
The PR description must reference DESIGN.md §11.3, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
Cost dashboard per prompt-version cost.
