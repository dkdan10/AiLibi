# Agent Prompt — 4.5 MeetingView

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.5 — MeetingView, anchored to DESIGN.md §5, DESIGN.md §7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-meetingview`
**Depends on:** 4.4 merged + mid-phase DTO audit passed
**Section refs:** DESIGN.md §5, DESIGN.md §7
**Complexity:** Medium

Transcript renderer for one meeting: reports + accusation rounds +
ballots + contradiction flags. Activated when the replay's current
tick is inside a meeting window.

**Files in scope:**
- frontend/src/components/MeetingView.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/src/store/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] MeetingView renders the full transcript exposed by the API DTOs: per-speaker reports with structured claims, statements per round, ballots with rationale text, contradiction flags inline.
- [ ] Prose `rationale_text` and `free_text` are foregrounded; structured fields are secondary.
- [ ] Prompt version + per-call cost are surfaced (small metadata footer per meeting).
- [ ] Component consumes the shared store/API shape from 4.3.
- [ ] Frontend build/check command passes.

## Implementation hint

See DESIGN.md §5. React component for meeting transcript + ballots. The MeetingView is hidden when the current tick is outside any meeting; replace MapView (or overlay on top of it — implementing agent picks based on layout sketch). Document the choice in `## Decisions`.

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
Open a PR from branch `phase-4-meetingview` with a title like `task 4.5: meetingview`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5, DESIGN.md §7), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
