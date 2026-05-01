# Codex Prompt — 3.P3 Accusation round prompt

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §5.2, DESIGN.md §5.3. Do not implement work outside these references.

3. Files in scope
You may edit only:
- agents/strategic/prompts/accusation_round.j2

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] Accusation round prompt exists and targets the Statement schema.
- [ ] Prompt uses rendered memory view, transcript-so-far, and contradiction flags only.
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
Open a PR from branch `phase-3-accusation-round-prompt` with a title like `task 3.P3: accusation round prompt`.
The PR description must reference DESIGN.md §5.2, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
agents/strategic/prompts/accusation_round.j2.
