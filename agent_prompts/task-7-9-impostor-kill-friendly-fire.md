# Agent Prompt — 7.9 Teammate-aware impostor kill + engine friendly-fire guard

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-7.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 7.9 — Teammate-aware impostor kill + engine friendly-fire guard, anchored to audits/audit-2026-06-01-1425-gameplay-data.md (gp-1, gp-3, MECH-B-1, MECH-B-2, D-D-1, F-F-1); DESIGN.md §3.4 (kill resolution); locked decision 6 (FSM tactical determinism). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-7.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-7-impostor-kill-friendly-fire`
**Depends on:** none (Wave 0.5 repair; the Wave-0 substrate 7.1–7.8 is merged)
**Section refs:** audits/audit-2026-06-01-1425-gameplay-data.md (gp-1, gp-3, MECH-B-1, MECH-B-2, D-D-1, F-F-1); DESIGN.md §3.4 (kill resolution); locked decision 6 (FSM tactical determinism)
**Complexity:** Medium

The 2026-06-01 gameplay-data audit found the committed 7p/2i eval set is balance-invalid: in 39 of 50 games an impostor kills its own teammate (35% of all 111 resolved kills), which fully explains the 38-9 / 76%-crew split — in the 39 self-destruct games impostors won 0, in the 11 clean games they won 9. The cause is two-layered and this task closes both. At the agent layer, `agents/tactical/impostor_policy.py::_scored_targets` (audit cites lines 264-329) ranks every sighted player with no teammate filter, even though `self_state.fellow_impostor_ids` is already on the observation packet (`observation/service.py:101`, landed by 7.2). At the engine layer, `engine.rules.resolve_kill` only checks the actor is an IMPOSTOR and never checks the target is a CREWMATE, so a friendly-fire kill is legal and resolves. This is the gating blocker for re-recording a trustworthy eval set.

The task also folds in the audit's gp-3 (co-location gate): 16 kills were queued against an out-of-room target and engine-rejected ("kill requires same room"), wasting the impostor's turn — the policy must not emit a kill intent unless the target is in the actor's current room. And it adds a light coordination heuristic for the tick-1 mutual-spawn case (10 games open with both impostors targeting each other in CAFETERIA on tick 1): two co-located impostors must not both emit a kill on the same tick.

Because the engine guard re-resolves recorded kill actions on playback, the existing committed `replays/samples/7p2i/` set (39 recorded teammate-kills) can no longer reconstruct byte-identically — those kills are now rejected, the per-tick `state_hash` diverges, and `load_replay` raises. This task therefore SKIPS exactly one test — `test_committed_7p2i_set_reconstructs_byte_identically` in `tests/api/test_replay_loader.py` — with an explicit reason; the post-7.9 re-record re-records a clean set and re-enables it (restoring its committed ≥ 30 resolved-meeting floor). The 4p/1i baseline is unaffected (one impostor, no friendly fire). The DESIGN.md §3.4 friendly-fire reconciliation is design-thread-owned and handled separately (the design thread tightens §3.4's kill rule to require a CREWMATE target; tracked in the Wave 0.5 Merge Criteria).

**Files in scope:**
- agents/tactical/impostor_policy.py (exclude `self_state.fellow_impostor_ids` from `_scored_targets`; gate kill intent on target co-location; tick-1 mutual-kill coordination heuristic — all deterministic)
- engine/rules.py (`resolve_kill` rejects a kill whose target is an IMPOSTOR — defense-in-depth; existing actor-is-impostor / same-room / cooldown checks unchanged)
- tests/agents/ + tests/engine/test_rules.py (teammate never selected; out-of-room kill never emitted; engine rejects an IMPOSTOR-target kill; an invariant test that no resolved kill has `victim_role == IMPOSTOR` across seeded games)
- tests/api/test_replay_loader.py (skip ONLY `test_committed_7p2i_set_reconstructs_byte_identically` with a reason referencing this guard + the pending re-record; leave `test_committed_7p2i_set_holds_crew_firewall` and the hermetic tmp_path multi-impostor tests untouched — they do not reconstruct the committed bytes)

**Files NOT in scope:**
- observation/service.py (`fellow_impostor_ids` is plumbed by 7.2 — consume it, do not edit)
- DESIGN.md (design-thread-owned; the §3 friendly-fire note is the design thread's)
- meetings/, eval/, llm/ (untouched)
- replays/samples/ (the re-record is a separate operational step after this merges; do not regenerate data here, and never delete the 4p/1i set)

**Definition of done:**
- [ ] `_scored_targets` excludes every id in `self_state.fellow_impostor_ids` before ranking; an impostor never selects a fellow impostor as a kill target.
- [ ] The policy emits a kill action only when the target is in the actor's current room (no "kill requires same room" rejections originate from the policy's own intents).
- [ ] Two co-located impostors do not both emit a kill on the same tick; the tick-1 mutual-spawn self-destruct cannot occur. Determinism is preserved (no RNG that would break replay reconstruction).
- [ ] `engine.rules.resolve_kill` rejects a kill whose target is an IMPOSTOR with a clear `ActionRejected` reason; the actor-is-impostor, same-room, and cooldown checks are unchanged; the legitimate impostor-kills-crewmate path still resolves.
- [ ] An invariant test asserts no resolved kill has `victim_role == IMPOSTOR` across a representative seeded set. Repro anchors: seed 4 tick 1 (mutual, CAFETERIA), seed 0 tick 7 (mid-game, MEDBAY), seed 32 tick 1.
- [ ] Exactly one test is skipped — `test_committed_7p2i_set_reconstructs_byte_identically` — with an explicit reason (the guard rejects the old set's recorded teammate-kills → `state_hash` drift; re-enabled by the post-7.9 re-record). Its sibling `test_committed_7p2i_set_holds_crew_firewall` is seed-derived and role-pure (it never reconstructs recorded ticks) and stays green; the hermetic tmp_path multi-impostor recon/firewall tests regenerate under the new rules and stay green; the 4p/1i reconstruction + leak suites stay green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Read `_scored_targets` and the packet's `self_state.fellow_impostor_ids`; filter teammates from the candidate set, then drop targets not co-located. For the engine guard, mirror the existing same-room/cooldown reject in `resolve_kill` with a target-role check. For the tick-1 coordination heuristic, keep it deterministic with no shared state: when a fellow impostor is co-located and would also emit a kill on the same tick, the lower-id impostor emits and the higher-id defers (`min(actor_id, fellow_id)` acts) — a pure function of ids, replay-safe, no RNG. Keep the FSM tactical layer deterministic (DESIGN.md §4 / locked decision 6) — this is target selection plus a reject, not new LLM behavior. The audit's MECH-B-3 "player is dead" same-tick rejection count shrinks automatically once teammate-kills stop (it was a downstream symptom). Confirm the 4p/1i frozen set still reconstructs after the change (the teammate filter and guard are no-ops at one impostor).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import llm.ollama_client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import observation.packet.SelfView"`
- `uv run python -c "import orchestrator.game"`
- `uv run python -c "import eval.meeting_quality"`

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
Open a PR from branch `phase-7-impostor-kill-friendly-fire` with a title like `task 7.9: teammate-aware impostor kill + engine friendly-fire guard`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-2026-06-01-1425-gameplay-data.md (gp-1, gp-3, MECH-B-1, MECH-B-2, D-D-1, F-F-1); DESIGN.md §3.4 (kill resolution); locked decision 6 (FSM tactical determinism)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
