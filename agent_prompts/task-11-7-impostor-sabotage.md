# Agent Prompt — 11.7 Impostor SabotageIntent emission in the impostor policy

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-11.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 11.7 — Impostor SabotageIntent emission in the impostor policy, anchored to DESIGN.md §3.4 (impostor actions), §4.4 (impostor FSM); experiments/lab/report-vent-escape-lab.md (the 11.1 vent-wiring precedent). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-11.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-11-impostor-sabotage`
**Depends on:** 11.5 (needs the working gating target + reads the public GlobalView task/sabotage fields)
**Section refs:** DESIGN.md §3.4 (impostor actions), §4.4 (impostor FSM); experiments/lab/report-vent-escape-lab.md (the 11.1 vent-wiring precedent)
**Complexity:** Integration

Make the impostor USE the lever. Mirror the 11.1 vent wiring: a new SABOTAGE branch in the `decide` cascade,
placed BELOW the in-vent-exit and COVER-or-vent branches but ABOVE the kill/stalk block, with a
`_sabotage(kind)` intent builder mirroring `_kill`/`_vent` and the FSM docstring updated. Trigger
deterministically from already-observed signals: emit `SabotageIntent("reactor")` when no sabotage is
active (guard via the public `global_status`) AND the crew is near a task win (read `tasks_completed`/
`tasks_total` from `global_status`, threshold anchored to "imminent crew win") — the strongest structural
use: it converts a near-certain task-win into a forced crew scramble + a hard loss timer. Keep it
conservative (do NOT sabotage every cooldown tick — that starves kills and is a degenerate low-interest
pattern); the impostor still hunts. The predicate MUST be a pure function of observed `global_status`/
`cooldown_status` (no RNG, no module state) so replays stay byte-identical.

**Files in scope:**
- agents/tactical/impostor_policy.py (the SABOTAGE branch; an `_active_sabotage(events)` guard; a `_sabotage(kind)` intent builder mirroring `_kill`/`_vent`; the deterministic trigger predicate over `global_status`; FSM docstring update; add `SabotageIntent` to the action-intent import)
- tests/agents/test_impostor_policy.py (emits `SabotageIntent("reactor")` when the crew is near a task win and no sabotage is active; does NOT emit when one is already active; the predicate is a pure function of observed `global_status`; in-vent/COVER/kill still pre-empt sabotage; sole- and multi-impostor cases)

**Files NOT in scope:**
- engine/**, observation/** (11.5)
- agents/tactical/crewmate_policy.py (11.6)
- agents/strategic/prompts/**, meetings/** (no meeting-layer change this wave)
- replays/samples/**, tests/fixtures/** (11.8)
- the FROZEN list

**Definition of done:**
- The impostor emits `SabotageIntent("reactor")` strategically (primary: deny an imminent crew task win; the predicate is deterministic + documented), never when a sabotage is already active, and never as per-tick spam that starves kills.
- In-vent exit, COVER-or-vent, and an available kill all out-prioritize sabotage; the decision stays a pure function of memory + `PublicMapView`.
- `bash scripts/check.sh` green.

## Implementation hint
Mirror the 11.1 vent wiring (a new cascade branch + an intent builder + a docstring rewrite), reading only
memory/`PublicMapView`, all tie-breaks deterministic, no RNG. Anchor the task-completion threshold to
"imminent crew win" and document the anchor. Avoid the degenerate "sabotage every cooldown tick" loop.

## Integration risk
Shares no file with 11.6, so they parallelize after 11.5. The danger is a low-interestingness degenerate
loop (sabotage-spam or sabotage-then-camp) — keep the predicate conservative and verify at 11.8 that R5
diversity RISES (a new IMPOSTOR_SABOTAGE shape appears) rather than collapsing into a farmed pattern.
Changes recorded bytes (11.8), not the hand-scripted fixtures.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import observation.packet.GlobalView"`

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
Open a PR from branch `phase-11-impostor-sabotage` with a title like `task 11.7: impostor sabotageintent emission in the impostor policy`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.4 (impostor actions), §4.4 (impostor FSM); experiments/lab/report-vent-escape-lab.md (the 11.1 vent-wiring precedent)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
