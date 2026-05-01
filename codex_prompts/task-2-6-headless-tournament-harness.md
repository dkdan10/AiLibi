# Codex Prompt — 2.6 Headless tournament harness

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §11.3. Do not implement work outside these references.

3. Files in scope
You may edit only:
- scripts/run_tournament.py
- eval/balance_eval.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] Headless tournament harness runs multiple games.
- [ ] Balance eval reports win rates across seeds.
- [ ] 100-game headless tournament completes without crashes.
- [ ] Both sides win > 20% of games.
- [ ] Leak test still passes across all tournament games.
- [ ] ruff check . passes.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Files explicitly NOT in scope:
- engine/ core rule changes
- agents/tactical/ policy changes
- llm/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-2-headless-tournament-harness` with a title like `task 2.6: headless tournament harness`.
The PR description must reference DESIGN.md §11.3, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
scripts/run_tournament.py, eval/balance_eval.py per §11.3.
