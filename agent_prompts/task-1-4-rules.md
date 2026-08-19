# Agent Prompt — 1.4 Rules

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-1.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 1.4 — Rules, anchored to DESIGN.md §3.4, DESIGN.md §3.5. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-1.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-1-rules`
**Depends on:** 1.3.5 merged
**Section refs:** DESIGN.md §3.4, DESIGN.md §3.5
**Complexity:** Medium

engine/rules.py for kill, vent, report, sabotage, win conditions per §3.4 + §3.5.

**Files in scope:**
- engine/rules.py
- engine/win_conditions.py

**Files NOT in scope:**
- agents/
- observation/
- api/
- frontend/
- llm/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Kill, vent, report, emergency meeting, sabotage, and win-condition rules match DESIGN.md §3.4 and §3.5.
- [ ] Invalid actions raise or emit rejection as specified; no silent fallbacks.
- [ ] Relevant engine tests pass.
- [ ] mypy --strict passes on touched engine files.
- [ ] ruff check . passes.

## Implementation hint

See DESIGN.md §3.4 + §3.5. Rule resolvers in `engine/rules.py` return typed `EngineEvent` subclasses directly (kill → KilledEvent, vent → VentEnteredEvent | VentExitedEvent, etc.). Win conditions in `engine/win_conditions.py` evaluate in the §3.5 order. Reject with `ActionRejectedError` for invalid actions; raise `ValueError` for invariant violations.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-1-rules` with a title like `task 1.4: rules`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.4, DESIGN.md §3.5), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
