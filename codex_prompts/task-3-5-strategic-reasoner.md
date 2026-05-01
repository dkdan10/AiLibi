# Codex Prompt — 3.5 Strategic reasoner

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §4.4. Do not implement work outside these references.

3. Files in scope
You may edit only:
- agents/strategic/reasoner.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] Strategic reasoner calls render_for_prompt, invokes LLMClient, and parses structured outputs.
- [ ] Strategic calls occur only at meeting or specified trigger points.
- [ ] No imports from engine/ under agents/.
- [ ] No LLM calls in agents/tactical/.
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
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-3-strategic-reasoner` with a title like `task 3.5: strategic reasoner`.
The PR description must reference DESIGN.md §4.4, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
agents/strategic/reasoner.py - wires render_for_prompt -> LLM -> parsed output.
