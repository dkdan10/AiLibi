# Agent Prompt — 4.4.5 MapView full

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.4.5 — MapView full, anchored to DESIGN.md §7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-mapview-full`
**Depends on:** 4.4 merged + mid-phase DTO audit passed
**Section refs:** DESIGN.md §7
**Complexity:** Medium

Expand MapView from the vertical slice into the full spectator view:
sabotage state, vent network, body markers, smooth interpolation
between ticks.

**Files in scope:**
- frontend/src/components/MapView.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/src/store/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Sabotage visualization (lights-out reduces room visibility per DESIGN.md §8.1).
- [ ] Vent network rendered (static graph from the DTO).
- [ ] Body markers appear at the room where a kill was reported (the body's room is in the meeting trigger DTO, not the kill event itself — role/kill attribution stay in the engine, not the DTO).
- [ ] Smooth interpolation between adjacent ticks (configurable tween duration).
- [ ] Component consumes the shared store/API shape from 4.3. No raw engine imports.
- [ ] Frontend build/check command passes.

## Implementation hint

See DESIGN.md §7 (frontend). PixiJS canvas renders rooms by `position` + `size` from the sanitized layout DTO. Use PixiJS `Ticker` for the tween; tween targets are the next tick's room positions.

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
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
Open a PR from branch `phase-4-mapview-full` with a title like `task 4.4.5: mapview full`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
