# Codex Prompt — 1.3.5 Engine contract hardening

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan hardening task anchored to DESIGN.md §3.1, DESIGN.md §3.2, and DESIGN.md §11.1. Do not implement work outside these references.

3. Files in scope
You may edit only:
- engine/world.py
- tests/engine/test_world_state.py
- tests/engine/test_map_loader.py
- tests/engine/test_actions.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] WorldState keeps the public field names players, bodies, tasks, and cooldowns but converts mutable mapping inputs into read-only mappings during construction.
- [ ] Mutating the original input dictionaries after WorldState construction does not mutate the WorldState.
- [ ] In-place mutation through state.players, state.bodies, state.tasks, and state.cooldowns raises instead of silently changing state.
- [ ] Baseline tests cover load_canonical_map(), map graph helpers, and canonical map counts.
- [ ] Baseline tests cover the Action union and invalid payload rejection.
- [ ] No kill, vent, report, sabotage, win-condition, tick, visibility, observation, agent, API, frontend, or LLM behavior is implemented.
- [ ] uv run pytest tests/engine/test_world_state.py tests/engine/test_map_loader.py tests/engine/test_actions.py passes.
- [ ] uv run ruff check . passes.
- [ ] uv run mypy --strict engine observation agents passes.
- [ ] uv run pytest passes.
- [ ] uv run lint-imports passes.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
This is a contract-hardening task, not a rules task.
If using MappingProxyType or another read-only wrapper, avoid sharing mutable backing dictionaries that outside callers can mutate after WorldState construction.
Files explicitly NOT in scope:
- engine/rules.py
- engine/tick.py
- observation/
- agents/
- api/
- frontend/
- llm/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-1-engine-contract-hardening` with a title like `task 1.3.5: engine contract hardening`.
The PR description must reference DESIGN.md §3.1, DESIGN.md §3.2, and DESIGN.md §11.1, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
Harden the already-merged engine state/action contracts before rules depend on them. Make WorldState defensively immutable and add baseline tests for map loading, action validation, and WorldState immutability.
