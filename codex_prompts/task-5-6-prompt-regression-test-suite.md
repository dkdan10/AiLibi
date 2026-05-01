# Codex Prompt — 5.6 Prompt regression test suite

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §11.3. Do not implement work outside these references.

3. Files in scope
You may edit only:
- eval/TODO_REVIEW prompt regression test file
- tests/TODO_REVIEW prompt regression fixtures path

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] Prompt regression tests exercise prompt versions against stable fixtures.
- [ ] Regression results are tagged by prompt version.
- [ ] Relevant eval tests pass.
- [ ] ruff check . passes.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Files explicitly NOT in scope:
- engine/
- agents/tactical/
- llm/ provider behavior
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-5-prompt-regression-test-suite` with a title like `task 5.6: prompt regression test suite`.
The PR description must reference DESIGN.md §11.3, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
Prompt regression test suite.
