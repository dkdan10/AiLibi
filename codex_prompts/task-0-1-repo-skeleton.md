# Codex Prompt — 0.1 Repo skeleton

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §2. Do not implement work outside these references.

3. Files in scope
You may edit only:
- pyproject.toml
- .gitignore
- engine/__init__.py
- observation/__init__.py
- agents/__init__.py
- agents/tactical/__init__.py
- agents/strategic/__init__.py
- agents/strategic/prompts/
- agents/memory/__init__.py
- meetings/__init__.py
- orchestrator/__init__.py
- llm/__init__.py
- api/__init__.py
- eval/__init__.py
- scripts/
- tests/__init__.py
- tests/test_smoke.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] pyproject.toml declares Python 3.11 and lists pydantic v2, fastapi, pytest, mypy, ruff, import-linter, hypothesis as dependencies.
- [ ] All packages from DESIGN.md §2 exist with empty __init__.py.
- [ ] tests/test_smoke.py has one passing test.
- [ ] pytest exits 0.
- [ ] ruff check . exits 0.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Files explicitly NOT in scope:
- any logic in any package
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-0-skeleton` with a title like `task 0.1: repo skeleton`.
The PR description must reference DESIGN.md §2, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
Create pyproject.toml, engine/, agents/, observation/, meetings/, orchestrator/, llm/, api/, eval/, tests/. Empty __init__.py files. Smoke test passes.
