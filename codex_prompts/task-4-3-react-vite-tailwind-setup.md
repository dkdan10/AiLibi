# Codex Prompt — 4.3 React + Vite + Tailwind setup

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §7. Do not implement work outside these references.

3. Files in scope
You may edit only:
- frontend/package.json
- frontend/vite.config.ts
- frontend/src/App.tsx
- frontend/src/api/client.ts
- frontend/src/store/index.ts

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] React, Vite, and Tailwind frontend skeleton exists.
- [ ] Type-safe API client exists.
- [ ] Shared store interface is defined before component fan-out.
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
- api/ beyond API client contract needs
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-4-react-vite-tailwind-setup` with a title like `task 4.3: react + vite + tailwind setup`.
The PR description must reference DESIGN.md §7, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
frontend/ skeleton, type-safe API client.
