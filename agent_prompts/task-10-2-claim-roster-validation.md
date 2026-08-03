# Agent Prompt — 10.2 Claim roster validation

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.2 — Claim roster validation, anchored to DESIGN.md §5.2, §6.3; audits/audit-2026-06-10-1820-gameplay-data.md gp-6 (C-C-8, H-H-6). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-claim-roster-validation`
**Depends on:** 10.1 (shares the belief-fold seam)
**Section refs:** DESIGN.md §5.2, §6.3; audits/audit-2026-06-10-1820-gameplay-data.md gp-6 (C-C-8, H-H-6)
**Complexity:** Medium

The fb3cfa5 guard validates accusation targets and ballot targets against the living roster, but
alibi.subject and corroboration.supports are unvalidated: the 9B emitted subjects like
"headless-seed-9" (a game id as a player), and 15 corroboration claims with invalid supports
were silent no-ops — which is why belief Rule 3 (corroboration lowers suspicion) has NEVER fired
in any recorded set. Garbage subject rows also leak into the §6.6 suspicion-graph render (seed
12 m2 renders "headless-seed-12:meeting-0:turn-0" as a player row at suspicion 0.46). Extend the
DROP + marker pattern to every subject-bearing claim field and filter the belief fold + graph
render to roster ids.

**Files in scope:**
- meetings/manager.py (extend the fb3cfa5 _drop_invalid_accusation_targets pattern to alibi.subject and corroboration.supports — invalid values DROP the claim and record the original on free_text via the existing marker convention)
- agents/memory/store.py + agents/memory/beliefs.py (filter the post-meeting evidence fold and the rendered suspicion graph to roster player ids — no garbage rows in beliefs or prompts)
- tests/meetings/test_manager.py + tests/agents/test_memory_store.py + tests/agents/test_beliefs.py (the acceptance shapes below)

**Files NOT in scope:**
- meetings/schemas.py (no schema shape change — DROP + marker, like fb3cfa5)
- agents/strategic/prompts/** (10.3 owns prompts)
- replays/samples/**, eval/** (re-record is 10.5)

**Definition of done:**
- [ ] An alibi whose subject is not a roster player, and a corroboration whose supports is not a roster player, are dropped at the meeting layer with the original preserved on free_text via the marker convention. The seed-9 m1 turns 2-3 shape ("headless-seed-9" as subject/supports) reproduces the drop in a test.
- [ ] The corroboration channel demonstrably FIRES end-to-end: a valid corroboration claim lowers the supported player's suspicion by the Rule-3 delta through the post-meeting fold — pinned in a game-loop integration test (the first live Rule-3 path; today it is structurally dead).
- [ ] The suspicion-graph render and the belief fold carry roster ids only: the seed-12 m2 garbage-row shape cannot render into any vote prompt.
- [ ] A corroboration naming a DEAD roster player is dropped (the seed-40 "p-2 dead" shape) — same rule as accusations.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Mirror fb3cfa5 exactly — one validation chokepoint in the manager, DROP + marker, no schema
change. Ordering is load-bearing relative to 10.1: the chokepoint validation runs BEFORE
detection and before the post-meeting fold, so a dropped garbage subject never mints a
contradiction flag, never consumes any 10.1 cap accounting, and never materializes a belief
row — assert that ordering in a test rather than assuming it. The graph-render and fold
filters are the defense-in-depth backstop: even if a garbage subject slips a future claim
type, the prompt surface and belief store stay clean. Rule 3's first firing is the contract's
real deliverable; the integration test proving suspicion moves -0.05 through a real meeting is
the hard line.

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
Open a PR from branch `phase-10-claim-roster-validation` with a title like `task 10.2: claim roster validation`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.2, §6.3; audits/audit-2026-06-10-1820-gameplay-data.md gp-6 (C-C-8, H-H-6)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
