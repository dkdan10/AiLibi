# Codex Prompt — 3.4 Meeting state machine

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §5.1, DESIGN.md §5.2. Do not implement work outside these references.

3. Files in scope
You may edit only:
- meetings/manager.py
- meetings/transcript.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] MeetingManager follows trigger lifecycle in DESIGN.md §5.1.
- [ ] Protocol implements report intake, accusation rounds, voting, and resolution per DESIGN.md §5.2.
- [ ] Missed deadlines yield default no-statement behavior as specified.
- [ ] Relevant meeting tests pass.
- [ ] mypy --strict passes on touched files.
- [ ] ruff check . passes.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Files explicitly NOT in scope:
- engine/ core rule changes
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-3-meeting-state-machine` with a title like `task 3.4: meeting state machine`.
The PR description must reference DESIGN.md §5.1, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
meetings/manager.py and meetings/transcript.py per §5.1 + §5.2.
