# Codex Prompt — 1.5 advance_tick

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §3.1. Do not implement work outside these references.

3. Files in scope
You may edit only:
- engine/tick.py
- engine/rng.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] advance_tick follows the seven-step loop in DESIGN.md §3.1.
- [ ] RNG state is explicitly threaded through engine/rng.py.
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
Open a PR from branch `phase-1-advance-tick` with a title like `task 1.5: advance_tick`.
The PR description must reference DESIGN.md §3.1, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
Pure function (state, actions) -> (state', events) per §3.1. RNG threaded through engine/rng.py.
