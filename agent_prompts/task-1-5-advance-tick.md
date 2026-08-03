# Agent Prompt — 1.5 advance_tick

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-1.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 1.5 — advance_tick, anchored to DESIGN.md §3.1. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-1.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-1-advance-tick`
**Depends on:** 1.4 merged
**Section refs:** DESIGN.md §3.1
**Complexity:** Integration

Pure function (state, actions) -> (state', events) per §3.1. RNG threaded through engine/rng.py.

**Files in scope:**
- engine/tick.py
- engine/rng.py

**Files NOT in scope:**
- agents/
- observation/
- api/
- frontend/
- llm/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] advance_tick follows the seven-step loop in DESIGN.md §3.1.
- [ ] RNG state is explicitly threaded through engine/rng.py.
- [ ] Relevant engine tests pass.
- [ ] mypy --strict passes on touched engine files.
- [ ] ruff check . passes.

## Implementation hint

See DESIGN.md §3.1. `advance_tick(state, actions, *, game_map) -> (state', events)` is a pure function implementing the 7-step loop. Steps 4–5 (observation packets, action solicitation) are explicitly the orchestrator's job; the engine just leaves placeholders. RNG state is threaded through `engine/rng.py::EngineRng`.

## Integration risk

advance_tick is the heartbeat of the entire simulation; every downstream Phase depends on it being a pure function with no hidden state. Risks:

- Determinism: any randomness must come from `state.rng_state`.   No `time.time()`, no `random.random()` without seed.
- MEETING phase: when an action triggers MEETING, return early;   do not run passive effects or win checks within that tick.
- Cooldown skip: the impostor that just killed must not have its   cooldown decremented in the same tick that set it.

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
Open a PR from branch `phase-1-advance-tick` with a title like `task 1.5: advance_tick`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.1), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
