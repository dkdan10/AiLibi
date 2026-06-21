# Agent Prompt — 13.5 Belief-band wiring for the new STRONG inferential classes

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.5 — Belief-band wiring for the new STRONG inferential classes, anchored to experiments/lab/report-phase-b-plan.md (belief-band); agents/memory/beliefs.py (`apply_contradiction_rule`, `contradiction_lift_key`, `MEETING_CONTRADICTION_LIFT_CAP`, the `+0.05 < 0.10` gate-distance invariant). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-belief-band`
**Depends on:** 13.3, 13.4
**Section refs:** experiments/lab/report-phase-b-plan.md (belief-band); agents/memory/beliefs.py (`apply_contradiction_rule`, `contradiction_lift_key`, `MEETING_CONTRADICTION_LIFT_CAP`, the `+0.05 < 0.10` gate-distance invariant)
**Complexity:** Integration
**Files in scope:**
- agents/memory/beliefs.py
- tests/agents/test_beliefs.py
**Files NOT in scope:**
- meetings/transcript.py — the detector + flag classes (13.2–13.4) are consumed, not changed
- the §4.6 gate / tally / SKIP logic — untouched
- engine/ and recordings — NO re-record

Route the new STRONG contradiction classes (cross-speaker `alibi_conflict` from 13.3, `alibi_vs_physical` from 13.4)
through `agents/memory/beliefs.py::apply_contradiction_rule` so a LONE inferential atom lands sub-gate (it INFORMS but
cannot eject alone) and only the TWO-SOURCE conjunction reaches the full `CONTRADICTION_SUSPICION_DELTA=0.3`. Preserve the
`contradiction_lift_key` dedup, `MEETING_CONTRADICTION_LIFT_CAP=0.3`, and the `+0.05 < 0.10` gate-distance invariant. No
gate / tally / SKIP change. NOTE: the new strong flags do not fire on the committed data yet (the 13.4 gate found 0) —
this is the PLUMBING that converts them to votes once the Wave-B game-changers (13.6–13.8) feed the detector richer
testimony, so it is validated by UNIT tests now (constructed flags), not by a re-extraction.
**Definition of done:** the new STRONG classes route through `apply_contradiction_rule` with a lone atom sub-gate and the
two-source conjunction at the full 0.3; a unit test confirms one lone new-class flag lifts a baseline 0.50 listener to
< 0.60 (cannot eject alone) while the conjunction crosses 0.60; `contradiction_lift_key` dedup + the 0.3 cap + the
gate-distance invariant are preserved (tested); no §4.6 gate / tally / SKIP change; the existing belief + leak +
determinism tests stay green; NO re-record; `scripts/check.sh` is green.

## Implementation hint
extend `apply_contradiction_rule`'s existing weak/strong handling to the new kinds rather than adding a parallel path; a
lone new-class atom takes the same sub-gate inform delta as a weak flag, the two-source conjunction takes the full 0.3;
reuse `contradiction_lift_key` so atoms of one contradiction cannot stack past the cap.

## Integration risk
the gate-distance invariant (`+0.05 < 0.10`) is load-bearing — a lone new-class atom that reaches 0.60 alone reopens the
single-signal wrong-ejection path the weak delta closed, so keep the full 0.3 strictly behind the two-source conjunction.
Belief-layer only: no §4.6 / tally / SKIP edit, no re-record, byte-determinism + firewall intact.

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
Open a PR from branch `phase-13-belief-band` with a title like `task 13.5: belief-band wiring for the new strong inferential classes`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing experiments/lab/report-phase-b-plan.md (belief-band); agents/memory/beliefs.py (`apply_contradiction_rule`, `contradiction_lift_key`, `MEETING_CONTRADICTION_LIFT_CAP`, the `+0.05 < 0.10` gate-distance invariant)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
