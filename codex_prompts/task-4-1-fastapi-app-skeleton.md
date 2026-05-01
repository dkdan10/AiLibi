# Codex Prompt — 4.1 FastAPI app skeleton

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §7. Do not implement work outside these references.

3. Files in scope
You may edit only:
- api/main.py
- api/routes/games.py
- api/routes/replays.py
- api/routes/eval.py
- api/routes/__init__.py
- api/ws.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] FastAPI app skeleton exists.
- [ ] Basic routes and WebSocket endpoint are registered per DESIGN.md §7.
- [ ] API remains a thin adapter.
- [ ] Relevant API tests pass if present.
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
Open a PR from branch `phase-4-fastapi-app-skeleton` with a title like `task 4.1: fastapi app skeleton`.
The PR description must reference DESIGN.md §7, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
api/main.py, basic routes, WebSocket endpoint per §7.
