# Codex Prompt — 3.7 Contradiction detection

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §5.4, DESIGN.md §6.4. Do not implement work outside these references.

3. Files in scope
You may edit only:
- meetings/transcript.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] detect_contradictions flags incompatible alibi and saw-player claims.
- [ ] Contradiction flags are information, not verdicts.
- [ ] Detected contradictions can be surfaced to rendered memory.
- [ ] Relevant transcript tests pass.
- [ ] mypy --strict passes on touched files.
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
Open a PR from branch `phase-3-contradiction-detection` with a title like `task 3.7: contradiction detection`.
The PR description must reference DESIGN.md §5.4, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
meetings/transcript.py::detect_contradictions per §5.4 + §6.4.
