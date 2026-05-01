# Codex Prompt — 2.2 Memory scaffolding (no LLM)

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §6.1. Do not implement work outside these references.

3. Files in scope
You may edit only:
- agents/memory/episodic.py
- agents/memory/working.py
- agents/memory/beliefs.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] Episodic, working, and belief memory scaffolds exist per DESIGN.md §6.1.
- [ ] Write paths are implemented; prompt rendering is not implemented in this task.
- [ ] No imports from engine/ under agents/.
- [ ] mypy --strict agents/ passes for touched files.
- [ ] ruff check . passes.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Files explicitly NOT in scope:
- engine/
- llm/
- agents/memory/store.py
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-2-memory-scaffolding` with a title like `task 2.2: memory scaffolding (no llm)`.
The PR description must reference DESIGN.md §6.1, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
agents/memory/episodic.py, working.py, beliefs.py per §6.1. Write paths only; no rendering yet.
