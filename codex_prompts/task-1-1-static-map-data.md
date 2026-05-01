# Codex Prompt — 1.1 Static map data

You are working on AiLibi. Before starting, read AGENTS.md, then read DESIGN.md and CODEX_IMPLEMENTATION.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, and CODEX_IMPLEMENTATION.md is the build plan.

2. Exact section reference
Implement the existing MVP-plan task anchored to DESIGN.md §3, DESIGN.md §8.1. Do not implement work outside these references.

3. Files in scope
You may edit only:
- engine/world.py

Read-only input:
- engine/maps/canonical_1.yaml

4. Acceptance criteria
The task is done only when all of these are true:
- [ ] engine/world.py loads and validates the existing human-provided engine/maps/canonical_1.yaml.
- [ ] Room graph and vent network from engine/maps/canonical_1.yaml are represented for one canonical MVP map.
- [ ] Relevant engine tests pass.
- [ ] mypy --strict passes on touched engine files.
- [ ] ruff check . passes.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
Read engine/maps/canonical_1.yaml as a supplied artifact only. Do not create, regenerate, reformat, or rewrite it.
If engine/maps/canonical_1.yaml is missing or structurally incompatible with DESIGN.md, stop and add a Questions section in the PR rather than guessing.
Files explicitly NOT in scope:
- engine/maps/canonical_1.yaml; do not modify, read and validate only
- agents/
- observation/
- api/
- frontend/
- llm/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

6. Output expectation
Open a PR from branch `phase-1-static-map-data` with a title like `task 1.1: static map data`.
The PR description must reference DESIGN.md §3, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.

Task
engine/world.py::Map, room graph, vent network. Use the human-provided engine/maps/canonical_1.yaml.
