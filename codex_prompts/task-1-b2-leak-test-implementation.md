# Codex Prompt — 1.B2 Leak test implementation

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §11.2, DESIGN.md §1.3. Do not implement work outside these references.

3. Files in scope
You may edit only:
- eval/leak_test.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] eval/leak_test.py asserts observation purity for hidden fields.
- [ ] Leak test runs against three scripted games.
- [ ] pytest eval/leak_test.py passes.
- [ ] No engine code is modified.
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
- api/
- frontend/
- llm/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-1-leak-test-implementation` with a title like `task 1.B2: leak test implementation`.
The PR description must reference DESIGN.md §11.2, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
Once ObservationPacket exists, implement the actual leak-test assertions. Can be done in parallel with task 1.8.
