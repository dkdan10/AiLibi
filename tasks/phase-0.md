# Phase 0 — Scaffolding

## Goal
Repo, CI, project skeleton, observation-firewall lint rule, skeleton leak test.

## Mechanism
Codex CLI, single agent, sequential.

## Tasks

### Task 0.1 — Repo skeleton
**Owner:** Codex CLI
**Branch:** phase-0-skeleton
**Depends on:** none
**Section refs:** DESIGN.md §2
**Files in scope:** pyproject.toml, .gitignore, all package __init__.py files, tests/test_smoke.py
**Files NOT in scope:** any logic in any package

**Definition of done:**
- [ ] `pyproject.toml` declares Python 3.11 and lists pydantic v2, fastapi, pytest, mypy, ruff, import-linter, hypothesis as dependencies.
- [ ] All packages from DESIGN.md §2 exist with empty `__init__.py`.
- [ ] `tests/test_smoke.py` has one passing test.
- [ ] `pytest` exits 0.
- [ ] `ruff check .` exits 0.

### Task 0.2 — CI workflow
**Owner:** Codex CLI
**Branch:** phase-0-ci
**Depends on:** 0.1 merged
**Section refs:** DESIGN.md §11
**Files in scope:** .github/workflows/ci.yml
**Definition of done:**
- [ ] CI runs ruff, mypy, pytest on every PR.
- [ ] CI passes on this PR.

### Task 0.3 — Import boundary lint
**Owner:** Codex CLI
**Branch:** phase-0-firewall
**Depends on:** 0.1 merged
**Section refs:** DESIGN.md §1.3
**Files in scope:** .importlinter, .github/workflows/ci.yml (extend), tests/test_firewall.py
**Definition of done:**
- [ ] `import-linter` config bans `agents.*` from importing `engine.*`.
- [ ] CI runs `lint-imports`.
- [ ] `tests/test_firewall.py` adds an intentional bad import in a temp file, runs lint-imports, asserts failure, removes the file.

### Task 0.4 — Skeleton leak test
**Owner:** Codex CLI
**Branch:** phase-0-leaktest
**Depends on:** 0.1 merged
**Section refs:** DESIGN.md §11.2
**Files in scope:** eval/leak_test.py
**Definition of done:**
- [ ] File exists with a single `@pytest.mark.skip(reason="implemented in phase 1")` test that documents the assertion contract.

### Task 0.5 — ADR
**Owner:** Codex CLI
**Branch:** phase-0-adr
**Depends on:** 0.1 merged
**Section refs:** DESIGN.md §0
**Files in scope:** docs/adr/0001-three-load-bearing-decisions.md
**Definition of done:**
- [ ] ADR captures the three load-bearing decisions verbatim with date and author.
