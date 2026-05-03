# Agent Prompt — 3.3 Memory rendering

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 3.3 — Memory rendering, anchored to DESIGN.md §6.6. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-memory-rendering`
**Depends on:** 3.2 merged
**Section refs:** DESIGN.md §6.6
**Complexity:** Medium

agents/memory/store.py::render_for_prompt per §6.6.

**Files in scope:**
- agents/memory/store.py
- tests/agents/test_memory_rendering.py
- tests/fixtures/memory_rendering/

**Files NOT in scope:**
- engine/
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `render_for_prompt` produces a token-budgeted structured view per DESIGN.md §6.6.
- [ ] Rendered memory comes from structured memory, not raw chat as source of truth.
- [ ] Salience ordering is deterministic and covered by golden tests.
- [ ] Rendered output includes open contradiction inputs when present.
- [ ] No imports from engine/ under agents/.
- [ ] `uv run mypy --strict agents meetings` passes.
- [ ] `uv run ruff check .` passes.

## Implementation hint

See DESIGN.md §6.6 for the canonical rendered-prompt example. The render function takes a `MemoryStore` and a token budget, then returns a single Markdown string with sections: role, tasks completed, recent observations (salience-sorted), beliefs, and open contradictions. Drop events past the token budget by lowest salience first.

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-3-memory-rendering` with a title like `task 3.3: memory rendering`.
The PR description must reference DESIGN.md §6.6, list the definition-of-done checklist, and include `Decisions` and (if blocking) `Questions` sections.
