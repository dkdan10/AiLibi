# Agent Prompt — 13.7 Graduated corroboration-aware testimony spread (R1/R3 lever)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.7 — Graduated corroboration-aware testimony spread (R1/R3 lever), anchored to experiments/lab/report-phase-b-plan.md (testimony-spread); agents/memory/beliefs.py (the pre-vote inform fold, `apply_meeting_evidence_rules`, `MeetingBeliefEvidence`, `TESTIMONY_INDEPENDENCE_BAR`); meetings/transcript.py (`independent_voices` — REUSED unchanged). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-testimony-spread`
**Depends on:** 13.5
**Section refs:** experiments/lab/report-phase-b-plan.md (testimony-spread); agents/memory/beliefs.py (the pre-vote inform fold, `apply_meeting_evidence_rules`, `MeetingBeliefEvidence`, `TESTIMONY_INDEPENDENCE_BAR`); meetings/transcript.py (`independent_voices` — REUSED unchanged)
**Complexity:** Integration
**Files in scope:**
- agents/memory/beliefs.py
- tests/agents/test_beliefs.py
**Files NOT in scope:**
- meetings/transcript.py — the `independent_voices` derivation is REUSED unchanged
- the detector / flag classes (13.2–13.5, consumed), prompts (13.6), visibility (13.8) — file-disjoint → parallel
- the §4.6 gate / tally / SKIP — untouched; engine/ + recordings — NO re-record

File-disjoint from the in-flight 13.6 (prompts) and 13.8 (visibility); it builds on 13.5's now-merged `beliefs.py` (hence
`depends on 13.5`, the shared-file edge). Replace the flat `+0.05` pre-vote inform with a graduated spread keyed on the
`independent_voices` COUNT: 1 voice → +0.05 (BYTE-IDENTICAL to today, so crew / no-witness games are unchanged); 2
INDEPENDENT voices → +0.12 (the first gate-cross — two corroborating observation-backed accounts can now move a 0.50
listener over 0.60); 3+ → cap +0.15. Persist only the flat +0.05 across rounds (no cross-round railroad). Keep
`TESTIMONY_INDEPENDENCE_BAR=2`; the `independent_voices` derivation in transcript.py is REUSED UNCHANGED. This is the
R1/R3 lever — it converts the richer shared testimony 13.6 elicits into ejections — so gate it explicitly on R1/R3
CONVERSION, NOT the win-split (decoupled) and NOT R7 (a separate channel).
**Definition of done:** the pre-vote inform is graduated by independent-voice count (1→+0.05, 2→+0.12, 3+→cap +0.15),
persisting only +0.05; `TESTIMONY_INDEPENDENCE_BAR=2` and the `independent_voices` derivation are unchanged; a unit test
confirms the 1-voice rung is BYTE-IDENTICAL to today (crew / no-witness games unmoved), 2 INDEPENDENT voices cross 0.60,
and a single corroboration-aligned opt-in alone cannot; no §4.6 gate / tally / SKIP change; the existing belief + leak +
determinism tests stay green; NO re-record (the R1/R3 conversion lift is measured at the Wave-B smoke re-record);
`scripts/check.sh` is green.

## Implementation hint
thread the `independent_voices` COUNT through `MeetingBeliefEvidence` + `apply_meeting_evidence_rules` (pre_vote) and map
it to the graduated delta; keep the 1-voice path byte-identical (the regression pin); reuse `independent_voices` from
transcript.py unchanged.

## Integration risk
this raises the stakes of any independence-filter bypass from a harmless +0.05 to a gate-crossing +0.12, so the
`independent_voices` bar is now load-bearing — do NOT loosen it, and persist only the flat +0.05 (a persisted +0.12 would
railroad across rounds). The 1-voice byte-identical pin guards the no-regression invariant. Belief-layer only: no §4.6 /
tally / SKIP edit, no re-record, firewall + determinism intact.

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
Open a PR from branch `phase-13-testimony-spread` with a title like `task 13.7: graduated corroboration-aware testimony spread (r1/r3 lever)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing experiments/lab/report-phase-b-plan.md (testimony-spread); agents/memory/beliefs.py (the pre-vote inform fold, `apply_meeting_evidence_rules`, `MeetingBeliefEvidence`, `TESTIMONY_INDEPENDENCE_BAR`); meetings/transcript.py (`independent_voices` — REUSED unchanged)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
