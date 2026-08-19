# Agent Prompt — 11.5 Task-gating sabotage: engine gate + reactor kind + public repair channel

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-11.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 11.5 — Task-gating sabotage: engine gate + reactor kind + public repair channel, anchored to DESIGN.md §3.1 (tick loop), §3.5 (win order), §8.3 (sabotage); engine/win_conditions.py:30-35 (the dormant IMPOSTOR_SABOTAGE). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-11.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-11-task-gating-sabotage`
**Depends on:** none (wave root)
**Section refs:** DESIGN.md §3.1 (tick loop), §3.5 (win order), §8.3 (sabotage); engine/win_conditions.py:30-35 (the dormant IMPOSTOR_SABOTAGE)
**Complexity:** Integration

Make a sabotage able to STALL the task race and surface its repair location publicly. ADD A NEW KIND
`reactor` (do NOT repurpose `lights`, which is load-bearing for the visibility system) declared in
`engine/maps/canonical_1.yaml` under `sabotages:` with a short fix-or-impostors-win `duration_ticks` (anchor
it to the map diameter — CAFETERIA→REACTOR hop count + `repair_ticks` — the way
`IMPOSTOR_PRETEND_TASK_DWELL_TICKS` is diameter-anchored; document the anchor in a YAML comment; it is NOT
the frozen task clock), `affected_visibility: same_room_and_adjacent` (base mode — reactor contests the
clock, not sightlines), two `repair_rooms` (e.g. REACTOR + ENGINEERING), and a new optional defaulted field
`gates_tasks: bool = False` on `SabotageDefinition` (so gating is declared in data, not by string-matching
`kind`, which the codebase deliberately avoids). Add `_tasks_gated(state, game_map)` returning
`sab.active and game_map.sabotages[sab.kind].gates_tasks`, and gate BOTH task paths: `_apply_do_task`
(reject with an `ActionRejectedError` when gated) and `_advance_tasks` (skip the progress increment / no
`TaskProgressed` event when gated). Thread `game_map` into both (the other appliers already receive it from
`_apply_action`/`advance_tick`). **No `engine/win_conditions.py` change** — `IMPOSTOR_SABOTAGE` already
fires on `active && remaining_ticks==0`; it becomes live purely through emission (11.7) + the short timer +
the gate. Surface the active sabotage's repair rooms + gating flag on the PUBLIC, role-blind `GlobalView`
so the crew (11.6) can route without `agents/`→`engine/` coupling.

**Files in scope:**
- engine/world.py (add `gates_tasks: bool = False` to `SabotageDefinition`; default keeps the loader contract byte-stable)
- engine/maps/canonical_1.yaml (add the `reactor` entry under `sabotages:`; do NOT touch the `tasks:` block / clock or the `lights` entry)
- engine/tick.py (the `_tasks_gated` helper; thread `game_map` into `_apply_do_task` + `_advance_tasks`; gate both the initiation and continuation paths; leave `_apply_sabotage`/`_advance_sabotage`/the win check unchanged)
- observation/packet.py (add `sabotage_repair_rooms: tuple[RoomId, ...] = ()` and `sabotage_is_gating: bool = False` to `GlobalView` — public, role-blind)
- observation/service.py (`_global_view`: populate the two new fields from `game_map.sabotages[kind]` when a sabotage is active)
- agents/perception.py (carry the two new fields through the `global_status` payload)
- tests/engine/test_tick.py (a `do_task` is rejected while a gating sabotage is active via BOTH paths; non-gating `lights` does NOT gate; repair clears the gate; IMPOSTOR_SABOTAGE fires end-to-end under a short reactor timer; same-tick repair still saves the crew)
- tests/engine/test_map_loader.py (the `reactor` kind loads; `gates_tasks` defaults False for `lights`)
- tests/observation/test_service.py (the new GlobalView fields populate only when a sabotage is active; default empty/false otherwise)

**Files NOT in scope:**
- agents/tactical/** (11.6/11.7 own the policies)
- engine/win_conditions.py (already correct — IMPOSTOR_SABOTAGE fires on active && remaining==0; no edit)
- engine/visibility.py (reactor uses base visibility — no visibility change)
- replays/samples/**, tests/fixtures/** (re-record is 11.8)
- the FROZEN list (§4.6 gate/threshold, tally/tie→SKIP, 2048/1024 caps, §6.3 constants, the task clock)

**Definition of done:**
- A gating sabotage halts task progress through BOTH `_apply_do_task` (rejection) and `_advance_tasks` (no progress event) while active; `lights` (non-gating) leaves task progress byte-identical to today.
- A reactor sabotage left to `remaining_ticks==0` with `active` true yields `IMPOSTOR_SABOTAGE`; a repair completing on the timer-expiry tick still saves the crew (the existing same-tick test still passes).
- `GlobalView.sabotage_repair_rooms`/`sabotage_is_gating` populate only when active and are identical across roles (leak-clean).
- `bash scripts/check.sh` green; firewall + leak-property sweeps pass.

## Implementation hint
Make `_tasks_gated` the single source of truth so the two task paths cannot drift. Thread `game_map` as a
pure pass-through (the other appliers already get it). Anchor reactor `duration_ticks` to map geometry and
document it; it is a sabotage timer, not the frozen task clock. Keep `gates_tasks` defaulted so `lights` and
every existing map-loader pin stay byte-stable.

## Public types this task introduces
- `observation.packet.GlobalView.sabotage_repair_rooms`
- `observation.packet.GlobalView.sabotage_is_gating`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk
The `game_map` signature change touches the hottest engine path — keep it a pure pass-through and confirm
the hand-scripted determinism/firewall fixtures (action-driven) still recompute identically (they are NOT
re-recorded; only policy-driven samples change, handled at 11.8). A reactor timer set too low is unwinnable
for crew, too high is unreachable — derive from geometry and validate at the 11.8 smoke; do NOT tune the
frozen task clock to compensate.

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
Open a PR from branch `phase-11-task-gating-sabotage` with a title like `task 11.5: task-gating sabotage: engine gate + reactor kind + public repair channel`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.1 (tick loop), §3.5 (win order), §8.3 (sabotage); engine/win_conditions.py:30-35 (the dormant IMPOSTOR_SABOTAGE)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
