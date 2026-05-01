# Codex Prompt — 4.2 Game broadcast

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §7. Do not implement work outside these references.

3. Files in scope
You may edit only:
- api/ws.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] WebSocket broadcaster streams tick events from a running game.
- [ ] Broadcast payloads are sanitized API DTOs, not raw engine internals.
- [ ] Relevant API/WebSocket tests pass if present.
- [ ] ruff check . passes.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Files explicitly NOT in scope:
- engine/ core logic
- agents/
- llm/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-4-game-broadcast` with a title like `task 4.2: game broadcast`.
The PR description must reference DESIGN.md §7, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
api/ws.py - broadcast tick events from a running game.
