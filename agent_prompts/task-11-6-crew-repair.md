# Agent Prompt — 11.6 Crew repair behavior in the crewmate policy

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-11.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 11.6 — Crew repair behavior in the crewmate policy, anchored to DESIGN.md §1.3 (firewall), §4.4 (crewmate FSM). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-11.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-11-crew-repair`
**Depends on:** 11.5 (consumes the new public GlobalView repair-rooms / gating channel)
**Section refs:** DESIGN.md §1.3 (firewall), §4.4 (crewmate FSM)
**Complexity:** Integration

Give the crew a reason to respond to a gating sabotage. The crewmate FSM (`crewmate_policy.py`) is a
priority cascade; add a REPAIR_SABOTAGE interrupt BELOW the body/kill interrupts (a meeting ends the round
anyway) but ABOVE the suspicion-walk and task routing (an unrepaired gating sabotage is a hard loss timer).
Detect via the freshest `global_status` (`sabotage_active`, `sabotage_kind`, and the new public
`sabotage_repair_rooms`/`sabotage_is_gating`) — reuse the existing memory-accessor pattern; the policy is
engine-free, so it reads repair rooms ONLY from the public `GlobalView` channel, never importing from
`engine/` and never hardcoding room names. When an active GATING sabotage exists: take one deterministic A*
step toward the nearest surfaced repair room (sorted-id tie-break), and emit `RepairSabotageIntent(kind)`
once in a repair room. Scope the diversion to `sabotage_is_gating` so `lights`-only games stay byte-identical.

**Files in scope:**
- agents/tactical/crewmate_policy.py (the REPAIR_SABOTAGE interrupt; an `_active_gating_sabotage(events)` accessor over the freshest `global_status`; a `_repair(kind)` intent builder mirroring `_do_task`; deterministic nearest-repair-room A* routing; docstring update; add `RepairSabotageIntent` to the action-intent import)
- tests/agents/test_crewmate_policy.py (the crewmate diverts + emits `RepairSabotageIntent` only for an active gating sabotage; ignores non-gating `lights`; deterministic room choice; body/kill interrupts still pre-empt repair)
- tests/observation/test_leak_property.py (the new GlobalView sabotage fields never differ by role; never carry role-bearing substrings)
- tests/api/test_leak.py (same role-invariance assertion through the packet API)

**Files NOT in scope:**
- engine/**, observation/** (11.5 owns the engine + the public channel)
- agents/tactical/impostor_policy.py (11.7)
- replays/samples/**, tests/fixtures/** (11.8)
- the FROZEN list

**Definition of done:**
- A crewmate observing an active gating sabotage walks one A* step/tick toward the nearest surfaced repair room and emits `RepairSabotageIntent(kind)` once there; the choice is deterministic and replay-stable.
- A non-gating sabotage (`lights`) does NOT trigger the diversion (lights-era crew behavior byte-identical).
- BODY_VISIBLE and KILL_WITNESSED interrupts still out-prioritize repair; the policy stays a pure function of memory + `PublicMapView` + `GlobalView`.
- `bash scripts/check.sh` green; the leak sweep confirms the new fields are role-invariant.

## Implementation hint
Mirror the existing accessor/interrupt structure and the deterministic min-hop tie-break used in
`ImpostorPolicy._choose_exit_vent`. Read repair rooms from the public `GlobalView` only. No cross-tick
tracker is needed — re-read the active-sabotage signal fresh each tick.

## Integration risk
Changes recorded bytes for policy-driven samples (11.8), not the hand-scripted fixtures. Watch for a
crewmate ping-ponging between equidistant repair rooms — the sorted tie-break must make the choice stable
across ticks. Keep the diversion gated on `sabotage_is_gating` so lights-only games stay byte-identical and
R5 attribution stays clean.

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
Open a PR from branch `phase-11-crew-repair` with a title like `task 11.6: crew repair behavior in the crewmate policy`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §1.3 (firewall), §4.4 (crewmate FSM)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
