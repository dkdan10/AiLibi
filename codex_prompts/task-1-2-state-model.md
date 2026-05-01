# Codex Prompt — 1.2 State model

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §3.2. Do not implement work outside these references.

3. Files in scope
You may edit only:
- engine/world.py
- engine/entities.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] WorldState, PlayerState, BodyState, TaskState, and SabotageState exist per DESIGN.md §3.2.
- [ ] Engine state models are immutable where required.
- [ ] Relevant engine tests pass.
- [ ] mypy --strict passes on touched engine files.
- [ ] ruff check . passes.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Files explicitly NOT in scope:
- agents/
- observation/
- api/
- frontend/
- llm/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-1-state-model` with a title like `task 1.2: state model`.
The PR description must reference DESIGN.md §3.2, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
WorldState, PlayerState, BodyState, TaskState, SabotageState per §3.2.
