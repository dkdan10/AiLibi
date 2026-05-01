# Codex Prompt — 1.8 Replay log

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §3.1, DESIGN.md §11.1, DESIGN.md §11.4. Do not implement work outside these references.

3. Files in scope
You may edit only:
- orchestrator/replay.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] Replay log writes JSONL entries containing tick, actions, and state hash per game.
- [ ] Replay output supports byte-identical determinism checks.
- [ ] Relevant replay/determinism tests pass.
- [ ] mypy --strict passes on touched files.
- [ ] ruff check . passes.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Files explicitly NOT in scope:
- agents/
- api/
- frontend/
- llm/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-1-replay-log` with a title like `task 1.8: replay log`.
The PR description must reference DESIGN.md §3.1, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
orchestrator/replay.py writes JSONL of (tick, actions, state-hash) per game.
