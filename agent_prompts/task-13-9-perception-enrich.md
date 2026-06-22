# Agent Prompt — 13.9 Enrich same-room perception: observed activity + co-presence + transitions (firewall-gated)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.9 — Enrich same-room perception: observed activity + co-presence + transitions (firewall-gated), anchored to the Wave-C smoke finding above (room-only starved the detector — fewer co-located witnesses → 0 alibi_vs_physical); observation/service.py (`_observed_actions_for_agent`, `_build_packet_from_visibility`); observation/packet.py (`PlayerView` = `{id, room, action}`); agents/perception.py (saw_player ingest); agents/memory/store.py (`_render_saw_player`, the 13.6 breadcrumb); the firewall — eval/leak_test.py (`_FORBIDDEN_VISIBLE_PLAYER_ACTIONS = {"sabotage"}`, visible_player keys EXACTLY `{id,room,action}`) + tests/observation/test_leak_property.py. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-perception-enrich`
**Depends on:** 13.6
**Section refs:** the Wave-C smoke finding above (room-only starved the detector — fewer co-located witnesses → 0 alibi_vs_physical); observation/service.py (`_observed_actions_for_agent`, `_build_packet_from_visibility`); observation/packet.py (`PlayerView` = `{id, room, action}`); agents/perception.py (saw_player ingest); agents/memory/store.py (`_render_saw_player`, the 13.6 breadcrumb); the firewall — eval/leak_test.py (`_FORBIDDEN_VISIBLE_PLAYER_ACTIONS = {"sabotage"}`, visible_player keys EXACTLY `{id,room,action}`) + tests/observation/test_leak_property.py
**Complexity:** Integration
**Files in scope:**
- observation/service.py
- agents/perception.py
- agents/memory/store.py
- tests/observation/test_service.py
- tests/observation/test_leak_property.py
- tests/agents/test_memory_store.py
- tests/agents/test_perception.py
**Files NOT in scope:**
- observation/packet.py `PlayerView` SCHEMA — do NOT add a key; reuse the existing `action` field for `"task"` (the leak test asserts visible_player keys are EXACTLY `{id,room,action}`). Co-presence + transitions are RENDER-only (store.py) from the episodic log — no packet field.
- engine/ — no engine change (the observation reads the existing world_state + the tick's submitted actions)
- meetings/transcript.py / agents/memory/beliefs.py / the §4.6 gate — the detector, suspicion deltas, and gate are UNCHANGED; this is the INPUT side only
- recordings — NO re-record here (the deduction/balance lift is the Wave-C combined smoke, paired with the rubric)

The smoke proved room-only crew STARVES the detector (fewer co-located witnesses → 0 alibi_vs_physical). Fix: keep the
room-only asymmetry (the impostor's edge) but make same-room observation HIGH-FIDELITY. Three firewall-gated,
vision-bounded enrichments:

1. **Observed activity (the fake-task lever).** When a player VISIBLE to the observer SUBMITTED a `do_task` this tick —
read from the TICK's submitted action list, NOT the resolved `last_action`, so a REJECTED attempt still counts — stamp the
observer's `PlayerView.action = "task"` (reuse the field; add no key). This is the cover mechanic: an impostor's
pretend-task `do_task` is engine-REJECTED (impostors own no instance) yet renders as `"task"` to observers,
BYTE-IDENTICAL to a crewmate's real task (cover) AND a falsifiable placement (deduction surface). **Gate by
role-sensitivity, not role:** `do_task` is role-BLIND (everyone tasks) so a submitted attempt shows regardless of
resolution; `kill`/`vent` stay WITNESS-gated (resolved events only — a rejected kill must NEVER surface, it would leak
impostor identity); `sabotage` is NEVER observable (`_FORBIDDEN_VISIBLE_PLAYER_ACTIONS`).

2. **Co-presence render.** In store.py render who the observer saw TOGETHER: `"[tick N] You saw p1 in Z (with p3, p4)."`
Pure render of the existing episodic `saw_player` sequence (same tick + room ⇒ co-present). Makes the LLM's
`saw_player.co_present` claim reliable → feeds `reconstruct_stated_paths` → the two-source material `alibi_vs_physical`
needs.

3. **Within-vision transitions.** Render entry/exit at the observer's own rooms: `"[tick N] p1 entered Z"` /
`"[tick N] p1 left Z"`, computed from consecutive `saw_player` deltas (present at N, gone at N+1 ⇒ left; absent at N,
present at N+1 ⇒ entered). The observer NEVER sees the adjacent origin/destination (room-only) — the full X→Y trajectory
emerges COLLECTIVELY when meeting testimony is combined (complements the 13.6 own-sightings breadcrumb).
**Definition of done:** a visible player's submitted `do_task` (resolved OR rejected) stamps `PlayerView.action="task"`,
vision-gated; a unit test asserts an impostor's rejected pretend-task and a crewmate's real task render BYTE-IDENTICAL to
every observer (no role leak); `kill`/`vent` stay witness-gated and `sabotage` stays non-observable (leak tests extended +
green; visible_player keys remain exactly `{id,room,action}`); store.py renders co-presence ("with …") + within-vision
transitions ("entered/left") with new goldens; the leak-property + leak_test sweeps + state-hash determinism stay green;
NO re-record; `scripts/check.sh` is green.

## Implementation hint
stamp `"task"` in `_observed_actions_for_agent` by scanning the TICK's submitted actions for VISIBLE players (NOT
`last_action`, so a rejected fake task counts); render co-presence + transitions in store.py from the episodic `saw_player`
log (no packet field); keep the `PlayerView` key set exactly `{id,room,action}`.

## Integration risk
FIREWALL is the whole risk surface — the new `"task"` annotation must be (a) vision-gated, (b) role-BLIND (real and fake
tasks render byte-identical — ASSERT it), (c) sabotage-EXCLUDED, and `kill`/`vent` must stay resolved-witness-gated (a
rejected kill surfacing would leak the impostor). Input side only — no detector/gate/belief change. Determinism: a pure
function of the visible submitted-action list + the episodic log, byte-stable. The deduction lift is real-Qwen-only →
gated at the Wave-C combined smoke with the new rubric; this task's offline bar is firewall + goldens + determinism.

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
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
Open a PR from branch `phase-13-perception-enrich` with a title like `task 13.9: enrich same-room perception: observed activity + co-presence + transitions (firewall-gated)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing the Wave-C smoke finding above (room-only starved the detector — fewer co-located witnesses → 0 alibi_vs_physical); observation/service.py (`_observed_actions_for_agent`, `_build_packet_from_visibility`); observation/packet.py (`PlayerView` = `{id, room, action}`); agents/perception.py (saw_player ingest); agents/memory/store.py (`_render_saw_player`, the 13.6 breadcrumb); the firewall — eval/leak_test.py (`_FORBIDDEN_VISIBLE_PLAYER_ACTIONS = {"sabotage"}`, visible_player keys EXACTLY `{id,room,action}`) + tests/observation/test_leak_property.py), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
