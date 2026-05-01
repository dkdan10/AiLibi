# Codex Prompt — 1.7 ObservationService

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §1.3, DESIGN.md §4.2. Do not implement work outside these references.

3. Files in scope
You may edit only:
- observation/service.py
- observation/packet.py
- observation/audit.py

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] ObservationPacket schema matches DESIGN.md §4.2.
- [ ] ObservationService is the only boundary crossing from engine truth to agent observations.
- [ ] Audit log records every packet.
- [ ] Relevant observation tests pass.
- [ ] mypy --strict passes on observation/.
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
Open a PR from branch `phase-1-observation-service` with a title like `task 1.7: observationservice`.
The PR description must reference DESIGN.md §1.3, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
observation/service.py and ObservationPacket schema per §1.3 + §4.2. Audit log to disk.
