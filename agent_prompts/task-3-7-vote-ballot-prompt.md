# Agent Prompt — 3.7 Vote ballot prompt

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 3.7 — Vote ballot prompt, anchored to DESIGN.md §5.5. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-vote-ballot-prompt`
**Depends on:** 3.3 merged
**Section refs:** DESIGN.md §5.5
**Complexity:** Small

agents/strategic/prompts/vote_ballot.j2.

**Files in scope:**
- agents/strategic/prompts/vote_ballot.j2

**Files NOT in scope:**
- engine/
- agents/tactical/
- llm/ client code
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Vote ballot prompt exists and targets the shared `VoteBallot` schema.
- [ ] Prompt receives rendered memory, transcript, contradiction flags, and suspicion graph.
- [ ] Prompt includes uncertainty-aware skip behavior.
- [ ] Prompt includes a version marker.
- [ ] No code outside the prompt file is modified.

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
Open a PR from branch `phase-3-vote-ballot-prompt` with a title like `task 3.7: vote ballot prompt`.
The PR description must reference DESIGN.md §5.5, list the definition-of-done checklist, and include `Decisions` and (if blocking) `Questions` sections.
