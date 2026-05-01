# Codex Prompt — 2.4 Crewmate FSM

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §4.4. Do not implement work outside these references.

3. Files in scope
You may edit only:
- agents/tactical/crewmate_policy.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] Crewmate FSM implements IDLE -> MOVE_TO_TASK -> DO_TASK -> IDLE and listed interrupts.
- [ ] Tactical decisions are deterministic and rule-based.
- [ ] No LLM calls in agents/tactical/.
- [ ] No imports from engine/ under agents/.
- [ ] Relevant agent tests pass.
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
- agents/tactical/impostor_policy.py
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-2-crewmate-fsm` with a title like `task 2.4: crewmate fsm`.
The PR description must reference DESIGN.md §4.4, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
agents/tactical/crewmate_policy.py per §4.4.
