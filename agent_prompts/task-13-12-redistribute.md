# Agent Prompt — 13.12 Redistribute the dead-crewmate task rule (replace drop), map-flag-gated

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.12 — Redistribute the dead-crewmate task rule (replace drop), map-flag-gated, anchored to experiments/lab/report-stopwatch-sweep.md (the validation) + experiments/lab/stopwatch_sweep.py (`_redistribute_apply_kill` — the validated logic); engine/tick.py:323-340 (the DROP in `_apply_kill`); orchestrator/game.py:850-859 (the DROP on ejection); engine/world.py (`Map` config + a new `dead_task_rule`); engine/maps/canonical_1.yaml; engine/entities.py:52 (`TaskState`: id/owner/map_task_id/room/progress/required_ticks/completed); DESIGN.md §3.5 (the dead-crewmate task rule). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-redistribute`
**Depends on:** none
**Section refs:** experiments/lab/report-stopwatch-sweep.md (the validation) + experiments/lab/stopwatch_sweep.py (`_redistribute_apply_kill` — the validated logic); engine/tick.py:323-340 (the DROP in `_apply_kill`); orchestrator/game.py:850-859 (the DROP on ejection); engine/world.py (`Map` config + a new `dead_task_rule`); engine/maps/canonical_1.yaml; engine/entities.py:52 (`TaskState`: id/owner/map_task_id/room/progress/required_ticks/completed); DESIGN.md §3.5 (the dead-crewmate task rule)
**Complexity:** Integration
**Files in scope:**
- engine/tick.py
- orchestrator/game.py
- engine/world.py
- engine/maps/canonical_1.yaml
- tests/engine/test_tick.py
- tests/orchestrator/test_game.py
**Files NOT in scope:**
- recordings — NO re-record here; the committed sets stay byte-identical under the DEFAULT `drop` flag. The redistribute re-record is 13.10.
- the §4.6 gate / detector / beliefs / visibility — unchanged
- agents/ and the observation packet — the recipient's new pending_task surfaces through the EXISTING owner-filtered SelfView channel; no agent-layer or packet change
- tests/observation/test_leak_property.py — the leak sweeps are RUN (must stay green), not edited (the re-key adds no new packet field)

Replace the dead-crewmate-task **DROP** with **REDISTRIBUTE**, behind a map config so the committed
replays stay byte-identical until the re-record. The validated logic (`_redistribute_apply_kill`): when a
crewmate dies (KILLED or EJECTED), instead of DELETING their incomplete task instances, RE-KEY each to a
LIVING CREWMATE — the burden does not shrink on death, but the crew stay active (the recipient must travel
to the task's room and finish it). **Recipient = the lowest-id living crewmate not already owning that map
task** (carry the instance's progress / room / required_ticks; change only `id` and `owner`); if every
living crewmate already owns it, fall back to dropping that one. Apply at BOTH death paths:
`engine/tick.py::_apply_kill` (the kill) and `orchestrator/game.py::apply_meeting_result` (the ejection).
Add `Map.dead_task_rule: Literal["drop","redistribute"]` (engine/world.py) read from canonical_1.yaml;
**DEFAULT "drop"** and keep canonical_1.yaml at "drop" so the committed replays + their state-hash verify
stay byte-identical — the 13.10 re-record is what flips canonical to "redistribute".

**Firewall:** the re-key is ENGINE-INTERNAL — the recipient's new `pending_task_id` reaches it through the
existing owner-filtered SelfView channel (its OWN task; no provenance, no role/attribution leak), and no
other agent can see it (own-task-only filter). The engine reading `player.role` to choose a crewmate
recipient is the same engine-side role access the win-conditions / kill-validation already use, never
exposed to agents. **Determinism:** lowest-id recipient + carried progress = byte-stable; a NEW
redistribute game re-sims to identical state hashes; committed replays (recorded under `drop`) re-walk
under `drop` byte-identically.
**Definition of done:** a `Map.dead_task_rule` config ("drop" | "redistribute"), default "drop", read from
canonical_1.yaml (kept at "drop"); under "redistribute" a dead crewmate's incomplete instances re-key to
the lowest-id living crewmate not already owning that map task (carry progress/room/required; new id+owner)
with the no-eligible-recipient drop fallback, at BOTH the kill and ejection paths (unit-tested for both);
under the default "drop" all behavior is UNCHANGED (committed replays + state-hash verify byte-identical);
the leak-property + leak_test sweeps stay green (no leak from the re-key); a unit test runs a "redistribute"
game twice and asserts identical state hashes; a redistributed task still counts toward CREWMATE_TASKS (the
recipient can complete it); NO re-record; `scripts/check.sh` is green.

## Implementation hint
port `experiments/lab/stopwatch_sweep.py::_redistribute_apply_kill` (re-add the dropped instances, re-keyed
to a living crewmate) gated on `game_map.dead_task_rule == "redistribute"`; mirror it in
`apply_meeting_result`; keep the existing drop-filter as the default branch so `drop` is byte-identical.

## Integration risk
behavior changes ONLY when the flag is "redistribute" — keep canonical DEFAULT "drop" so check.sh + the
committed state-hash verify stay green NOW (the redistribute re-record is 13.10). FIREWALL is the risk
surface: the re-key must add NO agent-visible provenance (the recipient's pending_task is leak-allowed —
assert the leak tests) and must not expose roles to agents (the role read is engine-side only).
DETERMINISM: lowest-id recipient + carry progress → assert a redistribute game re-sims identically.
Win-conditions unchanged: a redistributed instance still counts, so the crew can still win by tasks (harder).

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-13-redistribute` with a title like `task 13.12: redistribute the dead-crewmate task rule (replace drop), map-flag-gated`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing experiments/lab/report-stopwatch-sweep.md (the validation) + experiments/lab/stopwatch_sweep.py (`_redistribute_apply_kill` — the validated logic); engine/tick.py:323-340 (the DROP in `_apply_kill`); orchestrator/game.py:850-859 (the DROP on ejection); engine/world.py (`Map` config + a new `dead_task_rule`); engine/maps/canonical_1.yaml; engine/entities.py:52 (`TaskState`: id/owner/map_task_id/room/progress/required_ticks/completed); DESIGN.md §3.5 (the dead-crewmate task rule)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
