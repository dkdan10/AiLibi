# Agent Prompt — 4.4 MapView vertical slice

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.4 — MapView vertical slice, anchored to DESIGN.md §7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-mapview-vertical-slice`
**Depends on:** 4.3 merged
**Section refs:** DESIGN.md §7
**Complexity:** Small

A minimal MapView wired end-to-end against a real saved replay. Goal:
prove the API → store → component contract works before fanning out to
five components. Renders one PixiJS canvas with rooms as colored
rectangles and agent tokens that advance position as the replay's
current-tick index changes. No sabotage, no body markers, no vent
animation, no meeting overlay — those are 4.4b.

**Files in scope:**
- frontend/src/components/MapView.tsx
- frontend/src/components/RoomRect.tsx
- frontend/src/components/AgentToken.tsx
- frontend/src/App.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/src/store/index.ts (consumed read-only via the hook from 4.3)
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] App boots, lists available replays via the 4.2 endpoint, lets the user pick one.
- [ ] MapView renders rooms as PixiJS rectangles using room layout from the API DTO.
- [ ] Agent tokens render per-tick at the room they occupy in the current tick.
- [ ] A simple "next tick" / "previous tick" button advances the store's current-tick index; the canvas updates.
- [ ] Component consumes the shared store/API shape from 4.3. No direct engine/replay imports.
- [ ] Frontend build/check command passes.

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
Open a PR from branch `phase-4-mapview-vertical-slice` with a title like `task 4.4: mapview vertical slice`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
