# Agent Prompt — 2.8 Headless game orchestrator

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, AGENT_IMPLEMENTATION.md, and the task section in tasks/phase-2.md.

1. Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, AGENT_IMPLEMENTATION.md is the provider-neutral build plan, and the task contract below is the implementation contract for this PR.

2. Exact section reference
Implement Task 2.8 — Headless game orchestrator, anchored to DESIGN.md §1.4, DESIGN.md §3.1, DESIGN.md §11.4. Do not implement work outside these references.

3. Task contract
The authoritative task contract is copied below from tasks/phase-2.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-2-headless-game-orchestrator`
**Depends on:** 2.6 merged, 2.7 merged
**Section refs:** DESIGN.md §1.4, DESIGN.md §3.1, DESIGN.md §11.4

Build the deterministic single-game loop spine. This task wires existing engine,
observation, agents, action-intent translation, and replay together, but does
not implement tournament aggregation.

**Files in scope:**
- orchestrator/game.py
- orchestrator/seeder.py
- orchestrator/scheduler.py
- scripts/run_game.py
- tests/orchestrator/test_game.py
- tests/orchestrator/test_seeder.py

**Files NOT in scope:**
- engine/ core rule changes
- agents/tactical/ policy changes
- llm/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] A single headless game can run from a seed using deterministic role/spawn/task assignment.
- [ ] Each tick builds observations, dispatches agents, collects `ActionIntent`s, translates them to engine actions, advances the engine, and records replay entries.
- [ ] Meeting interruption and game-over states stop or pause the tick loop as appropriate for Phase 2.
- [ ] The orchestrator owns all engine imports; agents remain engine-free.
- [ ] Relevant orchestrator tests pass.
- [ ] `uv run mypy --strict engine observation agents orchestrator` passes.
- [ ] `uv run ruff check .` passes.

4. Pre-flight checklist
- Read AGENTS.md, DESIGN.md, AGENT_IMPLEMENTATION.md, and the task section before editing.
- Inspect the current implementation before editing.
- Confirm the dependency listed in the task contract is present in the current branch.
- Identify the existing local patterns for the files in scope and follow them.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
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
Open a PR from branch `phase-2-headless-game-orchestrator` with a title like `task 2.8: headless game orchestrator`.
The PR description must reference DESIGN.md §1.4, DESIGN.md §3.1, DESIGN.md §11.4, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.
