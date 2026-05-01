# Codex Prompt — 0.3 Import boundary lint rule

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §1.3. Do not implement work outside these references.

3. Files in scope
You may edit only:
- .importlinter
- .github/workflows/ci.yml
- tests/test_firewall.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] import-linter config bans agents.* from importing engine.*.
- [ ] CI runs lint-imports.
- [ ] tests/test_firewall.py adds an intentional bad import in a temp file, runs lint-imports, asserts failure, removes the file.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Files explicitly NOT in scope:
- engine/
- agents/ application logic
- observation/ application logic
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-0-firewall` with a title like `task 0.3: import boundary lint rule`.
The PR description must reference DESIGN.md §1.3, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
Add import-linter config that fails if agents/ imports from engine/. Verify by adding an intentional bad import in a test, watching CI fail, then removing it.
