# Agent Prompt — 1.1 Static map data

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-1.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 1.1 — Static map data, anchored to DESIGN.md §3, DESIGN.md §8.1. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-1.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-1-static-map-data`
**Depends on:** Phase 0 merged
**Section refs:** DESIGN.md §3, DESIGN.md §8.1
**Complexity:** Medium

engine/world.py::Map, room graph, vent network. Use the human-provided engine/maps/canonical_1.yaml.

**Files in scope (editable):**
- engine/world.py

**Read-only input:**
- engine/maps/canonical_1.yaml

**Files NOT in scope:**
- engine/maps/canonical_1.yaml; do not modify, read and validate only
- agents/
- observation/
- api/
- frontend/
- llm/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] engine/world.py loads and validates the existing human-provided engine/maps/canonical_1.yaml.
- [ ] Room graph and vent network from engine/maps/canonical_1.yaml are represented for one canonical MVP map.
- [ ] Relevant engine tests pass.
- [ ] mypy --strict passes on touched engine files.
- [ ] ruff check . passes.

## Implementation hint

See DESIGN.md §3 + §8.1. The canonical map ships at `engine/maps/canonical_1.yaml`; the loader lives in `engine/world.py::load_canonical_map`. Use PyYAML's `safe_load` — do not write a custom YAML parser. Validation happens via Pydantic model validators on `Map`.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-1-static-map-data` with a title like `task 1.1: static map data`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3, DESIGN.md §8.1), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
