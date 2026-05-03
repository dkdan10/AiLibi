# Phase 0 — Scaffolding

## Goal
Repo, CI, project skeleton, the lint rule that enforces the observation firewall, and a failing leak test.

## Parallelism
None. Single sequential agent (CLI preferred so you can watch).

## Tasks
### Task 0.1 — Repo skeleton
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
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] pyproject.toml declares Python 3.11 and lists pydantic v2, fastapi, pytest, mypy, ruff, import-linter, hypothesis as dependencies.
- [ ] All packages from DESIGN.md §2 exist with empty __init__.py.
- [ ] tests/test_smoke.py has one passing test.
- [ ] pytest exits 0.
- [ ] ruff check . exits 0.

**Ready-to-paste prompt:** `agent_prompts/task-0-1-repo-skeleton.md`

### Task 0.2 — CI workflow
**Branch:** `phase-0-ci`
**Depends on:** 0.1 merged
**Section refs:** DESIGN.md §11

.github/workflows/ci.yml running ruff, mypy, pytest. Triggers on PR.

**Files in scope:**
- .github/workflows/ci.yml

**Files NOT in scope:**
- AiLibi application logic
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] CI runs ruff, mypy, pytest on every PR.
- [ ] CI passes on this PR.

**Ready-to-paste prompt:** `agent_prompts/task-0-2-ci-workflow.md`

### Task 0.3 — Import boundary lint rule
**Branch:** `phase-0-firewall`
**Depends on:** 0.2 merged
**Section refs:** DESIGN.md §1.3

Add import-linter config that fails if agents/ imports from engine/. Verify by adding an intentional bad import in a test, watching CI fail, then removing it.

**Files in scope:**
- .importlinter
- .github/workflows/ci.yml
- tests/test_firewall.py

**Files NOT in scope:**
- engine/
- agents/ application logic
- observation/ application logic
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] import-linter config bans agents.* from importing engine.*.
- [ ] CI runs lint-imports.
- [ ] tests/test_firewall.py adds an intentional bad import in a temp file, runs lint-imports, asserts failure, removes the file.

**Ready-to-paste prompt:** `agent_prompts/task-0-3-import-boundary-lint-rule.md`

### Task 0.4 — Skeleton leak test
**Branch:** `phase-0-leaktest`
**Depends on:** 0.1 merged
**Section refs:** DESIGN.md §11.2

eval/leak_test.py imports nothing from engine/ directly but defines the test that will be implemented in Phase 1. Marked @pytest.mark.skip for now with a TODO.

**Files in scope:**
- eval/leak_test.py

**Files NOT in scope:**
- engine/
- agents/
- observation/ application logic
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] File exists with a single @pytest.mark.skip(reason="implemented in phase 1") test that documents the assertion contract.

**Ready-to-paste prompt:** `agent_prompts/task-0-4-skeleton-leak-test.md`

### Task 0.5 — ADR file
**Branch:** `phase-0-adr`
**Depends on:** 0.1 merged
**Section refs:** DESIGN.md §0

docs/adr/0001-three-load-bearing-decisions.md capturing DESIGN.md §0 verbatim.

**Files in scope:**
- docs/adr/0001-three-load-bearing-decisions.md

**Files NOT in scope:**
- AiLibi application logic
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] ADR captures the three load-bearing decisions verbatim with date and author.

**Ready-to-paste prompt:** `agent_prompts/task-0-5-adr-file.md`

## Merge Criteria
- All five tasks merged.
- CI green on main.
- You can clone the repo and pytest runs.
