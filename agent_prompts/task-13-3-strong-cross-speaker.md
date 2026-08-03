# Agent Prompt — 13.3 Cross-speaker alibi_conflict promoted STRONG (B2)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.3 — Cross-speaker alibi_conflict promoted STRONG (B2), anchored to experiments/lab/report-phase-b-plan.md (B2); experiments/lab/report-grounding-audit.md (the "add an inferential path" P1); meetings/transcript.py (`is_weak_contradiction`, the weak guards); audits/workflows/extract_gameplay_facts.py (re-extraction). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-strong-cross-speaker`
**Depends on:** 13.2
**Section refs:** experiments/lab/report-phase-b-plan.md (B2); experiments/lab/report-grounding-audit.md (the "add an inferential path" P1); meetings/transcript.py (`is_weak_contradiction`, the weak guards); audits/workflows/extract_gameplay_facts.py (re-extraction)
**Complexity:** Integration
**Files in scope:**
- meetings/transcript.py
- tests/meetings/test_contradictions.py
**Files NOT in scope:**
- the reconstruction helper (13.2 — consumed, not modified)
- agents/memory/beliefs.py — the belief delta for the new STRONG class is 13.5
- engine/ and the recorded replays — re-extraction only; NO re-record

In `meetings/transcript.py`, stop appending the WEAK marker to a genuinely-independent cross-speaker `alibi_conflict`
(two distinct non-subject speakers placing the same subject in two rooms over overlapping ticks). KEEP the adversarial /
self-pair / narrow / boundary weak guards VERBATIM (the adversarial guard exists because an impostor weaponised a
counter-alibi). Promote ONLY genuinely-independent cross-speaker conflicts → `is_weak_contradiction` returns False → the
extractor stamps `strong=True` → R7 lights on a pure re-extraction of the committed replays.
**Definition of done:** an independent cross-speaker `alibi_conflict` no longer carries the weak marker (the existing
weak guards unchanged + tested); RE-EXTRACTING the committed 9p2i replays and re-running `experiments/lab/rubric_score.py`
shows R7 > 0 on ≥ 2 seeds with EVERY new STRONG flag role-gated to a TRUE impostor (≈ 0 naming a crewmate, the gp-3
watch-the-games eyeball is a BLOCKING check); the wrong-ejection count does NOT rise vs the baseline (R4 floor); $0, NO
re-record; `scripts/check.sh` is green.

## Implementation hint
the flag simply carries no weak marker → `is_weak_contradiction` returns False → the extractor stamps `strong=True`; do
NOT touch `is_weak_contradiction` itself and keep the adversarial/self-pair/narrow/boundary guards byte-identical;
validate by re-extracting the committed replays (no recording changes).

## Integration risk
a STRONG flag that names a CREWMATE is a false positive that both Goodharts R7 and risks a wrong ejection (R4) — role-gate
every new STRONG flag and count STRONG-on-crewmate (must be ≈ 0); the adversarial weak-guard MUST stay verbatim or the
impostor games it; this changes the EXTRACTOR's output on re-extraction, NOT any recording — byte-determinism and the
firewall are untouched and there is NO re-record.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
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
Open a PR from branch `phase-13-strong-cross-speaker` with a title like `task 13.3: cross-speaker alibi_conflict promoted strong (b2)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing experiments/lab/report-phase-b-plan.md (B2); experiments/lab/report-grounding-audit.md (the "add an inferential path" P1); meetings/transcript.py (`is_weak_contradiction`, the weak guards); audits/workflows/extract_gameplay_facts.py (re-extraction)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
