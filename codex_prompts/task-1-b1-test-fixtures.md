# Codex Prompt — 1.B1 Test fixtures

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §11.1. Do not implement work outside these references.

3. Files in scope
You may edit only:
- tests/fixtures/scripted_game_*.json

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] Short canned scripted game fixtures exist for determinism testing.
- [ ] Fixtures use the stable action schema from task 1.3.
- [ ] No engine code is modified.
- [ ] pytest fixture-loading tests pass if present.
- [ ] ruff check . passes.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Files explicitly NOT in scope:
- engine/
- agents/
- observation/
- api/
- frontend/
- llm/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-1-test-fixtures` with a title like `task 1.B1: test fixtures`.
The PR description must reference DESIGN.md §11.1, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
Hand-author tests/fixtures/scripted_game_*.json short canned games used by the determinism test. Does not touch engine code.
