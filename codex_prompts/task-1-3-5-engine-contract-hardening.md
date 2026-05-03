# Codex Prompt — 1.3.5 Engine contract hardening

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, CODEX_IMPLEMENTATION.md, and the task section in tasks/phase-1.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, CODEX_IMPLEMENTATION.md is the build plan, and the task contract below is the implementation contract for this PR.

2. Exact section reference
Implement Task 1.3.5 — Engine contract hardening, anchored to DESIGN.md §3.1, DESIGN.md §3.2, DESIGN.md §11.1. Do not implement work outside these references.

3. Task contract
The authoritative task contract is copied below from tasks/phase-1.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-1-engine-contract-hardening`
**Depends on:** 1.3 merged
**Section refs:** DESIGN.md §3.1, DESIGN.md §3.2, DESIGN.md §11.1

Harden the already-merged engine state/action contracts before rules depend on them. Make WorldState defensively immutable and add baseline tests for map loading, action validation, and WorldState immutability.

**Files in scope:**
- engine/world.py
- tests/engine/test_world_state.py
- tests/engine/test_map_loader.py
- tests/engine/test_actions.py

**Files NOT in scope:**
- engine/rules.py
- engine/tick.py
- observation/
- agents/
- api/
- frontend/
- llm/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
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
Open a PR from branch `phase-1-engine-contract-hardening` with a title like `task 1.3.5: engine contract hardening`.
The PR description must reference DESIGN.md §3.1, DESIGN.md §3.2, DESIGN.md §11.1, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.
