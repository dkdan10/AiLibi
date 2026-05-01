# Codex Prompt — 0.4 Skeleton leak test

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §11.2. Do not implement work outside these references.

3. Files in scope
You may edit only:
- eval/leak_test.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] File exists with a single @pytest.mark.skip(reason="implemented in phase 1") test that documents the assertion contract.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Files explicitly NOT in scope:
- engine/
- agents/
- observation/ application logic
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-0-leaktest` with a title like `task 0.4: skeleton leak test`.
The PR description must reference DESIGN.md §11.2, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
eval/leak_test.py imports nothing from engine/ directly but defines the test that will be implemented in Phase 1. Marked @pytest.mark.skip for now with a TODO.
