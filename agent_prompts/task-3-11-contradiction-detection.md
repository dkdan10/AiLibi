# Agent Prompt — 3.11 Contradiction detection

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 3.11 — Contradiction detection, anchored to DESIGN.md §5.4, DESIGN.md §6.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-contradiction-detection`
**Depends on:** 3.10 merged
**Section refs:** DESIGN.md §5.4, DESIGN.md §6.4
**Complexity:** Medium

meetings/transcript.py::detect_contradictions per §5.4 + §6.4.

**Files in scope:**
- meetings/transcript.py
- tests/meetings/test_contradictions.py

**Files NOT in scope:**
- engine/
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `detect_contradictions` flags incompatible alibi and saw-player claims.
- [ ] Contradiction flags are information, not verdicts.
- [ ] Detected contradictions are represented in shared schemas and can be surfaced to rendered memory.
- [ ] Relevant transcript tests pass.
- [ ] `uv run mypy --strict meetings agents` passes.
- [ ] `uv run ruff check .` passes.

## Implementation hint

See DESIGN.md §5.4 + §6.4. Index alibi claims by (agent, tick_range, location); cross-reference with `saw_player` observations; emit `ContradictionRef` objects. Detector is data, not verdict — flags feed back into the rendered memory view (3.3).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import agents.strategic.reasoner"`
- `uv run python -c "import llm.budgeted_client"`
- `uv run python -c "import meetings.manager"`

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
Open a PR from branch `phase-3-contradiction-detection` with a title like `task 3.11: contradiction detection`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.4, DESIGN.md §6.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
