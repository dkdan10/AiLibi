# Codex Prompt — 3.2 Output schemas

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §5.3, DESIGN.md Appendix A. Do not implement work outside these references.

3. Files in scope
You may edit only:
- agents/strategic/output_schemas.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] ReportDocument, Statement, and VoteBallot schemas match DESIGN.md §5.3 and Appendix A.
- [ ] Schemas are suitable for structured LLM output.
- [ ] No imports from engine/ under agents/.
- [ ] mypy --strict agents/ passes for touched files.
- [ ] ruff check . passes.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Files explicitly NOT in scope:
- engine/
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-3-output-schemas` with a title like `task 3.2: output schemas`.
The PR description must reference DESIGN.md §5.3, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
agents/strategic/output_schemas.py - ReportDocument, Statement, VoteBallot per §5.3 + §A.
