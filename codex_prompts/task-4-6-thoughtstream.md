# Codex Prompt — 4.6 ThoughtStream

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §6, DESIGN.md §7. Do not implement work outside these references.

3. Files in scope
You may edit only:
- frontend/src/components/ThoughtStream.tsx

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] ThoughtStream displays per-agent memory and LLM reasoning/call information exposed by the spectator API.
- [ ] Component consumes the shared store/API shape from 4.3.
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
- api/
- frontend/src/store/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-4-thoughtstream` with a title like `task 4.6: thoughtstream`.
The PR description must reference DESIGN.md §6, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
Per-agent memory + LLM call viewer.
