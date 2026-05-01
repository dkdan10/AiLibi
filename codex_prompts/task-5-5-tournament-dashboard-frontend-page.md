# Codex Prompt — 5.5 Tournament dashboard frontend page

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §11.3, DESIGN.md §7. Do not implement work outside these references.

3. Files in scope
You may edit only:
- frontend/src/components/TournamentDashboard.tsx

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] Frontend dashboard renders the tournament JSON report.
- [ ] Dashboard includes metrics from 5.1 through 5.4.
- [ ] Frontend build/check command passes if configured.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Files explicitly NOT in scope:
- engine/
- agents/
- llm/
- api/ unless a read endpoint already exists and needs wiring
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-5-tournament-dashboard-frontend-page` with a title like `task 5.5: tournament dashboard frontend page`.
The PR description must reference DESIGN.md §11.3, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
Tournament dashboard frontend page.
