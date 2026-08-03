# Agent Prompt — 11.1 Wire vents into the impostor policy

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-11.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 11.1 — Wire vents into the impostor policy, anchored to DESIGN.md §1.3 (observation firewall), §3.4 (vents/visibility); experiments/lab/report-vent-escape-lab.md. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-11.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-11-impostor-vents`
**Depends on:** none (wave root)
**Section refs:** DESIGN.md §1.3 (observation firewall), §3.4 (vents/visibility); experiments/lab/report-vent-escape-lab.md
**Complexity:** Integration

The impostor FSM (`agents/tactical/impostor_policy.py`) emits only Kill/Move/DoTask/Wait, so the impostor
walks away from every kill and is SEEN — the offline counterfactual proved ~91% of the structured evidence
against impostors (35→3 flags) is exactly this post-kill sighting trail, which a vent would hide. The engine
already supports vents end-to-end (VERIFIED: `engine/tick.py:452-453` dispatches `VentAction` →
`_apply_vent`; `engine/rules.py:102-179` `resolve_vent`; 6 vents in `engine/maps/canonical_1.yaml:218-260`;
`orchestrator/boundary.py` round-trips any intent generically), so this task is policy logic + a self-state
field — NO engine or boundary edit. Add the impostor's vent decision: (a) POST-KILL VENT-ENTER — redesign
the COVER branch (`impostor_policy.py:196-198`, currently a move to the alphabetically-first neighbor) to
emit `VentIntent` when a vent is in the impostor's room, the impostor is not already `in_vent`, and NO
non-teammate witness is co-present this tick (reuse the kill gate's `latest_events` `saw_player` scan,
`impostor_policy.py:359-470` pattern; teammates in `fellow_impostor_ids` never count as witnesses) — else
fall back to the existing move-away; (b) IN-VENT VENT-EXIT — a new high-priority branch (gated on
`in_vent`, before the body/kill logic) that emits `VentIntent` to a connected vent whose room holds no
visible body, preferring the room toward the current best isolated target (`_scored_targets`), else the
alphabetically-first connected vent (deterministic, id/room-sorted, no RNG). `heard_vent_use` stays
observable (`observation/service.py` audible events), so a careless vent near a witness is a NEW catchable
tell — desirable (rubric R2 "deception sometimes fails"), do not suppress it beyond the witness guard above.
The impostor reads its own `in_vent` from a new `SelfView.in_vent` bool (the one shared-file seam with 11.3).

**Files in scope:**
- agents/tactical/impostor_policy.py (the COVER-or-vent rewrite, the in-vent vent-exit branch, a `_vent(vent_id)` intent builder mirroring `_kill`, a room→vent lookup over the public map's vent_rooms/vent_graph, and the FSM docstring update; all tie-breaks deterministic)
- observation/packet.py (add `in_vent: bool` to `SelfView` — a non-role-bearing self-state bool, firewall-clean)
- observation/service.py (populate `SelfView.in_vent` from `player.in_vent` at the self-view build)
- agents/perception.py (carry `in_vent` through the self-state payload)
- tests/agents/test_impostor_policy.py (the acceptance pins below; the `_public_map` helper currently sets vent_graph/vent_rooms empty — populate them)
- tests/observation/test_service.py + tests/observation/test_leak_property.py (in_vent surfaces only on SelfView; never leaks)

**Files NOT in scope:**
- engine/** (resolve_vent/_apply_vent/visibility VERIFIED correct — no engine edit)
- agents/strategic/prompts/**, meetings/** (11.2 owns prompt wiring)
- agents/memory/store.py (11.3 owns the kill-memory render)
- replays/samples/**, tests/fixtures/** (re-record is 11.4)

**Definition of done:**
- Vent-enter fires at the body when the impostor is alone (no non-teammate co-present), is suppressed when a non-teammate witness is co-present (falls back to move-away), and is skipped when no vent is in the room.
- In-vent vent-exit moves toward an isolated / non-body room; all choices deterministic and replay-stable.
- `SelfView.in_vent` is populated; the leak sweep confirms it appears only on the recipient's own SelfView.
- `bash scripts/check.sh` green; firewall + leak-property sweeps pass; no impostor can be left pathologically stuck in a vent (an in-vent impostor always has an exit branch).

## Implementation hint
Reuse the existing co-presence/witness scan the kill gate already runs on `latest_events` rather than a
parallel scan, so "no witness" means the same thing for kill and for vent. The vent-enter guard should
prefer a quiet WALK over a vent only when a walk is genuinely unseen; when a witness is already present, a
vent and a walk are equivalent exposure, so keep the simpler move-away fallback. Do not add a kill-cooldown
interaction (venting does not set cooldown) — the body-in-own-room check already precedes the kill check, so
vent-cover never competes with a same-tick kill.

## Public types this task introduces
- `observation.packet.SelfView.in_vent` (new field on the existing privileged self channel)`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk
The shared SelfView/packet/service/perception edit with 11.3 is the dependency edge (11.3 depends on this
task) — keep `in_vent` a plain bool so 11.3's `own_kill` addition is orthogonal. A vent changes recorded
bytes for policy-driven sample runs (handled at 11.4), but NOT the hand-scripted determinism/firewall
fixtures (action-driven, recomputed at runtime). Watch for an impostor that vents every tick and never
kills — the exit branch must resume normal stalking once repositioned.

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
Open a PR from branch `phase-11-impostor-vents` with a title like `task 11.1: wire vents into the impostor policy`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §1.3 (observation firewall), §3.4 (vents/visibility); experiments/lab/report-vent-escape-lab.md), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
