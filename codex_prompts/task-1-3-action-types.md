# Codex Prompt — 1.3 Action types

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md Appendix A. Do not implement work outside these references.

3. Files in scope
You may edit only:
- engine/actions.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] Action types are represented as a Pydantic union per DESIGN.md Appendix A.
- [ ] Validators reject invalid action payloads.
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
Open a PR from branch `phase-1-action-types` with a title like `task 1.3: action types`.
The PR description must reference DESIGN.md Appendix A, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
engine/actions.py Pydantic union per §A. Validators.
