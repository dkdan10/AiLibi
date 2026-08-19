# Agent Prompt — 13.5.1 Dead-code truth-up: relabel AgentRuntime + earmark WorkingMemory/alibi docstrings

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-13-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.5.1 — Dead-code truth-up: relabel AgentRuntime + earmark WorkingMemory/alibi docstrings, anchored to the 2026-06-25 memory-pipeline diagnosis (workflow `wg54kfoxy`; the cited structures verified to have ZERO production writers — a NEUTRAL classification); agents/runtime.py; agents/memory/working.py; agents/memory/beliefs.py (`record_alibi`, `PlayerBelief.alibis`); agents/memory/store.py (the `last_seen` render hook); orchestrator/game.py (`TacticalAgent`, the real production agent). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-5-dead-code-truthup`
**Depends on:** none
**Section refs:** the 2026-06-25 memory-pipeline diagnosis (workflow `wg54kfoxy`; the cited structures verified to have ZERO production writers — a NEUTRAL classification); agents/runtime.py; agents/memory/working.py; agents/memory/beliefs.py (`record_alibi`, `PlayerBelief.alibis`); agents/memory/store.py (the `last_seen` render hook); orchestrator/game.py (`TacticalAgent`, the real production agent)
**Complexity:** Small
**Files in scope:**
- agents/runtime.py
- agents/memory/working.py
- agents/memory/beliefs.py
- agents/memory/store.py
**Files NOT in scope:**
- tests/ — the relabel is docstring-only and keeps every public API byte-identical, so no test changes are needed; if a test breaks, STOP and report (the edit was not neutral)
- DESIGN.md and AGENT_IMPLEMENTATION.md — the doc reconciliation is the design thread's Wave A, not this task
- the substrate wiring — Wave C (13.5.2–13.5.5) wires these structures; this task only DOCUMENTS their current status and earmark, and must neither wire nor delete them

Three memory structures are wired into the composite memory surface but never written in
production (diagnosis-verified: zero non-test callers of `WorkingMemory.set_goal` /
`set_path` / `record_sighting` and `BeliefState.record_alibi`; `AgentRuntime` is a Phase-2 glue
stub whose `_choose_action` always returns `WaitIntent` and whose `_update_memory` is a no-op,
imported only by tests — the production agent is `orchestrator/game.py::TacticalAgent`). They are
NOT bugs and must NOT be deleted: they are the scaffolding Wave C wires (the alibi list ←
testimony-as-content; `working.last_seen` ← movement perception). This task makes the code
self-documenting about that status so a reader — and the Phase-14 migration author — is not
misled into thinking they are live or into deleting them. Strictly docstrings and `#` comments:
no logic, no signature, no public type, no render-output change.

Specifics: (1) `agents/runtime.py` — a loud module + class docstring stating `AgentRuntime` is a
TEST-ONLY harness (a Phase-2 scaffold), NOT the production agent, and naming
`orchestrator/game.py::TacticalAgent` as the real one; note `_choose_action` is a hardcoded
`WaitIntent` and `_update_memory` a no-op. (2) `agents/memory/working.py` — docstring states
`WorkingMemory` currently has no production writer (`_last_seen` is always empty at runtime) and
earmarks `last_seen` as wired by Wave C (movement perception). (3) `agents/memory/beliefs.py` —
docstrings on `record_alibi` and `PlayerBelief.alibis` state the list is written by no production
path and rendered nowhere today, earmarked for Wave C (testimony-as-content). (4)
`agents/memory/store.py` — a comment at the `last_seen` render hook noting the suffix never renders
today (no writer), populated by Wave C (movement perception).

**Definition of done:** `AgentRuntime` carries a module + class docstring identifying it as a
test-only harness and naming `orchestrator/game.py::TacticalAgent` as the production agent;
`WorkingMemory`, `record_alibi` / `PlayerBelief.alibis`, and the `store.py` `last_seen` hook each
carry a docstring or comment stating current dead status plus the Wave-C lever that will wire
them; NO logic, signature, public-type, or render-output change (a memory-render fixture is
byte-identical before and after); `git diff` shows only docstring/comment lines; the full
`scripts/check.sh` is green.

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
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-13-5-dead-code-truthup` with a title like `task 13.5.1: dead-code truth-up: relabel agentruntime + earmark workingmemory/alibi docstrings`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing the 2026-06-25 memory-pipeline diagnosis (workflow `wg54kfoxy`; the cited structures verified to have ZERO production writers — a NEUTRAL classification); agents/runtime.py; agents/memory/working.py; agents/memory/beliefs.py (`record_alibi`, `PlayerBelief.alibis`); agents/memory/store.py (the `last_seen` render hook); orchestrator/game.py (`TacticalAgent`, the real production agent)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
