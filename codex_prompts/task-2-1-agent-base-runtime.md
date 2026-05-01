# Codex Prompt — 2.1 Agent base + runtime

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §4.1. Do not implement work outside these references.

3. Files in scope
You may edit only:
- agents/base.py
- agents/runtime.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] AgentInterface protocol and AgentRuntime wiring match DESIGN.md §4.1.
- [ ] Runtime consumes ObservationPacket rather than engine state.
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
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-2-agent-base-runtime` with a title like `task 2.1: agent base + runtime`.
The PR description must reference DESIGN.md §4.1, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
agents/base.py and agents/runtime.py per §4.1. Memory wiring stub.
