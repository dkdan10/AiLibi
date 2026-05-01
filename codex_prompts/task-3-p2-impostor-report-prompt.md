# Codex Prompt — 3.P2 Impostor report prompt

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §4.5, DESIGN.md §5.3, DESIGN.md §6.6. Do not implement work outside these references.

3. Files in scope
You may edit only:
- agents/strategic/prompts/impostor_report.j2

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] Impostor report prompt exists and targets the ReportDocument schema.
- [ ] Prompt frames deception as a game rule without exposing hidden engine state.
- [ ] Prompt uses rendered memory view and public transcript inputs only.
- [ ] Prompt includes a version marker.
- [ ] No code outside the prompt file is modified.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Files explicitly NOT in scope:
- engine/
- agents/tactical/
- llm/ client code
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-3-impostor-report-prompt` with a title like `task 3.P2: impostor report prompt`.
The PR description must reference DESIGN.md §4.5, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
agents/strategic/prompts/impostor_report.j2.
