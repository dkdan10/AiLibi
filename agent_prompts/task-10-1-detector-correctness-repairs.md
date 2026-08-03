# Agent Prompt — 10.1 Detector correctness repairs

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.1 — Detector correctness repairs, anchored to DESIGN.md §5.4, §6.3; audits/audit-2026-06-10-1820-gameplay-data.md gp-2 (C-C-1, C-C-2, C-C-3, D-D-3). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-detector-correctness`
**Depends on:** none (repair root)
**Section refs:** DESIGN.md §5.4, §6.3; audits/audit-2026-06-10-1820-gameplay-data.md gp-2 (C-C-1, C-C-2, C-C-3, D-D-3)
**Complexity:** Integration

The contradiction detector is the crew's sole structured-evidence engine and 93% of what it
emits is artifact: 34 compound-room-label mismatches (a sighting room like "CAFETERIA/EAST_HALL"
string-compared against an alibi room), 11 placeholder-room comparisons, 31 endpoint-tick-only
window mismatches, and a flag-stacking defect that let 19 near-duplicate flags lift one innocent
to suspicion 1.0 (seed 9 m1). The alibi_conflict path never received the 9.7 weak
classification at all (9.7 covered alibi_vs_sighting only), so self-pairs and adversarial
testimony still carry full +0.3 deltas. Net effect measured on this set: the strong path fired
on 5 wrong ejections and 0 correct ones, and every one of the 11 wrong ejections rode this
engine. Repair the artifact classes, weak-classify the conflict path, and cap stacked lifts —
while keeping the 4 genuine CANON_INTERIOR impostor flags alive (the only genuinely diagnostic
signal the set produced).

**Files in scope:**
- meetings/transcript.py (canonicalize rooms at claim-parse before any comparison: split compound labels, treat placeholder/unknown rooms as no-room (no flag), containment reads as CONSISTENT and feeds the corroboration path instead of a conflict — a third-party sighting whose room sits inside the subject's stated alibi is corroboration-class evidence, magnitude at most the Rule-3 delta and capped once per (subject, claim); PREFER weak-banding endpoint-tick-only window mismatches over excluding them — an endpoint mismatch can still be a real signal under corroboration; exclude only with a documented reason, and either way the handling must stay deterministic; give _detect_alibi_conflicts the 9.7 weak classification — a self-pair (both claims by the subject) is weak, adversarial accuser-stated testimony about the subject is capped weak, a defense-echo (the subject restating their own alibi after an accusation) dedupes to the original claim instead of minting a new flag)
- agents/memory/beliefs.py (cap the contradiction lift at ONE weak delta per (subject, alibi-claim) pair and add a per-subject per-meeting transient cap so near-duplicate flags cannot stack to 1.0; strong flags keep their existing single-flag weight)
- tests/meetings/test_transcript.py + tests/agents/test_beliefs.py + tests/meetings/test_manager.py (the acceptance shapes below, as offline reconstructions against the committed bytes — replays do not change until 10.5)

**Files NOT in scope:**
- agents/strategic/prompts/** (10.3 owns prompt changes; the §4.6 render is FROZEN)
- meetings/manager.py claim-target validation (10.2 owns the roster-validation extension)
- the 9.8 accumulator constants in agents/memory/beliefs.py (frozen — this task touches the contradiction-lift path only)
- replays/samples/**, eval/** (re-record is 10.5; gate metrics are 10.4)

**Definition of done:**
- [ ] Room canonicalization: compound labels, placeholders, and containment no longer mint alibi_vs_sighting or alibi_conflict flags; containment-consistent pairs feed corroboration. Pinned against the committed bytes: the 34 compound-label and 11 placeholder artifact flags from the audit's facts no longer reproduce under the new detector.
- [ ] Endpoint-tick-only mismatches no longer carry full weight — weak-banded by preference (excluded only with a documented reason; deterministic either way). The 31 endpoint-fuzz flags from the audit collapse accordingly.
- [ ] The corroboration fold demonstrably ACCEPTS a detector-derived containment-consistent pair, not only a claim-stated CorroborationClaim — integration-pinned. The audit proved Rule 3 never fired, so detector-sourced corroboration is likely the second never-exercised ingestion path; a containment-consistent pair that silently no-ops would make the canonicalization half-inert.
- [ ] alibi_conflict is weak-classified: self-pairs weak, adversarial accuser-stated testimony capped weak, defense-echoes deduped to the original claim. Seeds 11 m2 and 17 m0 self-pairs land in the weak band; seed 9 m1 renders p-8 at 0.58 (19 flags collapse to 1 effective lift), not 1.0.
- [ ] Per-(subject, claim) lift dedup + per-subject per-meeting cap: no innocent reaches 1.0 from flag volume. Seed 26 m1: innocent p-6 no longer outscores impostor p-3.
- [ ] The genuine channel SURVIVES: the 4 CANON_INTERIOR impostor flags (seeds 3, 30, 42, 45) still fire as strong under the repaired detector — pinned individually. Killing artifacts must not kill detection.
- [ ] Determinism: the detector + lift math remain pure functions; re-running on the same transcript yields byte-identical flags.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Canonicalize ONCE at claim-parse so the detector, the corroboration path, and the renderer all
see the same canonical rooms — do not scatter normalization across comparison sites. The weak
classification helpers from 9.7 already exist in meetings/transcript.py; the conflict path
should call the same logic, not a parallel implementation. Acceptance pins run offline against
the committed replays via the replay-loader walk (the audit extractor shows the pattern), so
every number above is checkable for $0 before any re-record.

## Integration risk

This is the highest-leverage seam in the crew pipeline — every belief, render, and ballot
downstream reads it. The hard line is the CANON_INTERIOR survival pin: an over-aggressive
repair that silences the genuine channel converts "93% artifacts" into "100% silence" and
Wave 1 measures nothing. Recording-side only; committed reconstruction unaffected until 10.5.

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
Open a PR from branch `phase-10-detector-correctness` with a title like `task 10.1: detector correctness repairs`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.4, §6.3; audits/audit-2026-06-10-1820-gameplay-data.md gp-2 (C-C-1, C-C-2, C-C-3, D-D-3)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
