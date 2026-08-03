# Agent Prompt — 9.2 Impostor kill-intent room validation

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-9.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 9.2 — Impostor kill-intent room validation, anchored to DESIGN.md §3.4; audits/audit-2026-06-07-0717-gameplay-data.md gp-5 (findings MECH-B-1, A-A-3). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-9.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-9-kill-intent-room`
**Depends on:** none (hygiene root)
**Section refs:** DESIGN.md §3.4; audits/audit-2026-06-07-0717-gameplay-data.md gp-5 (findings MECH-B-1, A-A-3)
**Complexity:** Small

25 of 164 recorded kill attempts (15%, across 19/50 seeds) were engine-rejected "kill requires same
room": the tactical policy ranks `saw_player` sightings from ANY tick, so it emits KillIntent
against targets that already left (or dodge by id-order move resolution). A wasted kill attempt is
a wasted impostor tick and a confound on impostor-side reads. Validate the candidate against the
actor's CURRENT room at intent time.

**Files in scope:**
- agents/tactical/impostor_policy.py (the kill branch: emit KillIntent only when the chosen target is co-located with the actor THIS tick — re-validate the sighting against current-tick visibility before queuing; stale sightings remain valid for stalking/navigation, only the kill emission tightens)
- tests/agents/test_impostor_policy.py (a stale-sighting case: target seen earlier in another room → no KillIntent; a co-located case still kills; the teammate-exclusion cases stay green)

**Files NOT in scope:**
- engine/ (the same-room rule and id-order resolution are canon — DESIGN.md §3.4; the engine guard stays the backstop)
- agents/strategic/** (no prompt or reasoner change — the impostor build freeze holds)
- replays/samples/** (re-record is 9.5)

**Definition of done:**
- [ ] KillIntent is emitted only for a target whose current-tick observation places it in the actor's room; the stale-sighting regression test passes; no change to stalk/navigation scoring.
- [ ] The DESIGN.md §3.4 id-order canon is referenced in the kill-branch comment (the engine remains the enforcement; this is producer-side waste removal).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
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
Open a PR from branch `phase-9-kill-intent-room` with a title like `task 9.2: impostor kill-intent room validation`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.4; audits/audit-2026-06-07-0717-gameplay-data.md gp-5 (findings MECH-B-1, A-A-3)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
