# Codex Prompt — 0.1 Repo skeleton

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, CODEX_IMPLEMENTATION.md, and the task section in tasks/phase-0.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, CODEX_IMPLEMENTATION.md is the build plan, and the task contract below is the implementation contract for this PR.

2. Exact section reference
Implement Task 0.1 — Repo skeleton, anchored to DESIGN.md §2. Do not implement work outside these references.

3. Task contract
The authoritative task contract is copied below from tasks/phase-0.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-0-skeleton`
**Depends on:** none
**Section refs:** DESIGN.md §2

Create pyproject.toml, engine/, agents/, observation/, meetings/, orchestrator/, llm/, api/, eval/, tests/. Empty __init__.py files. Smoke test passes.

Preservation note: if engine/maps/canonical_1.yaml already exists, do not modify, replace, or delete it. Phase 0 may create missing package directories and __init__.py files, but must leave the map YAML untouched.

**Files in scope:**
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

**Files NOT in scope:**
- any logic in any package
- engine/maps/canonical_1.yaml if it already exists; preserve it unchanged
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] pyproject.toml declares Python 3.11 and lists pydantic v2, fastapi, pytest, mypy, ruff, import-linter, hypothesis as dependencies.
- [ ] All packages from DESIGN.md §2 exist with empty __init__.py.
- [ ] tests/test_smoke.py has one passing test.
- [ ] pytest exits 0.
- [ ] ruff check . exits 0.

4. Pre-flight checklist
- Read AGENTS.md, DESIGN.md, CODEX_IMPLEMENTATION.md, and the task section before editing.
- Inspect the current implementation before editing.
- Confirm the dependency listed in the task contract is present in the current branch.
- Identify the existing local patterns for the files in scope and follow them.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.
If something is ambiguous, stop and add a Questions section in the PR description rather than guessing.

6. Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

7. Output expectation
Open a PR from branch `phase-0-skeleton` with a title like `task 0.1: repo skeleton`.
The PR description must reference DESIGN.md §2, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.
