# Codex Prompt — 0.5 ADR file

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §0. Do not implement work outside these references.

3. Files in scope
You may edit only:
- docs/adr/0001-three-load-bearing-decisions.md

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] ADR captures the three load-bearing decisions verbatim with date and author.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Files explicitly NOT in scope:
- AiLibi application logic
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-0-adr` with a title like `task 0.5: adr file`.
The PR description must reference DESIGN.md §0, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
docs/adr/0001-three-load-bearing-decisions.md capturing DESIGN.md §0 verbatim.
