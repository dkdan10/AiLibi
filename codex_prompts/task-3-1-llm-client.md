# Codex Prompt — 3.1 LLM client

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §4.4, DESIGN.md §7. Do not implement work outside these references.

3. Files in scope
You may edit only:
- llm/client.py
- llm/claude_provider.py
- llm/cache.py
- llm/budget.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] LLMClient protocol exists.
- [ ] Provider adapter is behind LLMClient protocol.
- [ ] Prompt cache and per-game budget support exist.
- [ ] No LLM calls are added to agents/tactical/.
- [ ] mypy --strict passes on touched files.
- [ ] ruff check . passes.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Files explicitly NOT in scope:
- agents/tactical/
- engine/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-3-llm-client` with a title like `task 3.1: llm client`.
The PR description must reference DESIGN.md §4.4, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
llm/client.py, llm/claude_provider.py or provider equivalent, cache, budget.
