# Agent Prompt — 3.12 Meeting/orchestrator integration

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 3.12 — Meeting/orchestrator integration, anchored to DESIGN.md §3.1, DESIGN.md §5.1, DESIGN.md §11.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-meeting-orchestrator-integration`
**Depends on:** 3.11 merged
**Section refs:** DESIGN.md §3.1, DESIGN.md §5.1, DESIGN.md §11.4
**Complexity:** Integration

Apply `MeetingResult` through the orchestrator, resume gameplay, and record
meeting artifacts in replay/eval records.

**Files in scope:**
- orchestrator/game.py
- orchestrator/replay.py
- tests/orchestrator/test_meeting_integration.py
- tests/orchestrator/test_replay_meetings.py

**Files NOT in scope:**
- engine/ core rule changes
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Orchestrator applies `MeetingResult` ejection/skip outcomes to engine-owned world state.
- [ ] Gameplay resumes after meetings with tick/cooldown behavior matching DESIGN.md §3.1 and §5.1.
- [ ] Replay records meeting transcripts, ballots, contradiction flags, prompt versions, and LLM cost metadata.
- [ ] Engine remains pure; MeetingManager does not mutate engine state directly.
- [ ] **R-9 acceptance gate (per `audits/audit-2026-05-15-0225-reconciled.md` §R-9):** `ReplayEntry` — or its Phase 3 successor introduced by this task — records meeting transcripts, prompt versions, LLM outputs, and cost metadata per DESIGN.md §11.4. The replay-determinism test exercises at least one long-horizon replay (≥ 200 ticks or one full meeting cycle, whichever is longer) and asserts byte-for-byte identity. The existing short-horizon byte-identical test from Task 2.8 (`tests/orchestrator/test_game.py:139-155`) is preserved as a fast smoke check; it is not replaced.
- [ ] Relevant integration tests pass with fake LLM outputs.
- [ ] `uv run mypy --strict engine observation agents meetings orchestrator llm` passes.
- [ ] `uv run ruff check .` passes.

## Implementation hint

See DESIGN.md §3.1 + §11.4. The orchestrator owns the engine ↔ MeetingManager handoff: when the engine returns `phase == "MEETING"`, dispatch to MeetingManager, receive a `MeetingResult`, apply it to engine-owned state via a new engine function `apply_meeting_result(state, result)`, and resume. Replay log gains LLM-output records for replay determinism.

## Integration risk

This is the Phase 3 convergence point. It depends on tasks 3.1–3.11 plus 2.8.

- Determinism: replay must record LLM outputs alongside actions   and replay must re-use them, not re-call the model. Verify   with a determinism test that runs the same seed twice and   asserts byte-identical replay logs.
- Memory consistency: meeting outcomes must update each agent's   belief state. Without this, post-meeting reasoning is stale.
- Phase boundary: do not let MeetingManager touch engine state   directly — every state change goes through the orchestrator.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import agents.strategic.reasoner"`
- `uv run python -c "import llm.budgeted_client"`
- `uv run python -c "import meetings.manager"`

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
Open a PR from branch `phase-3-meeting-orchestrator-integration` with a title like `task 3.12: meeting/orchestrator integration`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.1, DESIGN.md §5.1, DESIGN.md §11.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
