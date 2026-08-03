# Agent Prompt — 10.15 Crew belief-spread lever (single-witness inform)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.15 — Crew belief-spread lever (single-witness inform), anchored to DESIGN.md §5.2, §6.3, §4.6; audits/audit-2026-06-13-1816-gameplay-data.md C-C-1 + H-4; the owner belief-spread-first decision (2026-06-14); [[project_ejection_suspicion_principle]]. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-belief-spread`
**Depends on:** 10.7 (extends the merged two-witness pre-vote fold; crew-side, file-disjoint from the impostor toolkit so it dispatches in parallel with it)
**Section refs:** DESIGN.md §5.2, §6.3, §4.6; audits/audit-2026-06-13-1816-gameplay-data.md C-C-1 + H-4; the owner belief-spread-first decision (2026-06-14); [[project_ejection_suspicion_principle]]
**Complexity:** Integration

The crew counterweight, OWNER-LOCKED to belief-spread (NOT a tally reweight — the lab re-run showed
V3 skip-halfweight degraded to +4 imp / +2 innocent on the honest W1 bytes, no longer free). The
dominant residual is the SKIP-plurality bloc: 37/59 over-gate-lost-plurality meetings where the
impostor is over-gate for ONE witness but the listeners stay under-gate, so the equal tally's SKIP
bloc wins. The 10.7 two-witness pre-vote fold underperformed (1/11 conversions) because two
independent observation-backed witnesses are rare in the single-accuser chain. The fix SPREADS a
single witness's first-hand testimony to the listeners — informing the majority so enough independently
cross 0.60 and the EQUAL tally convicts on its own. This honors the owner principle: the inform alone
cannot eject (it lifts near-gate listeners, never a baseline listener), so crossing still requires the
listener's own prior (accumulate-across-rounds) PLUS the witness's inform (corroborate-within-round) —
never a single signal, never a bare-verbal cascade.

**Files in scope:**
- meetings/transcript.py (extend the 10.7 voices/independence helper: a SINGLE relevance-passing first-hand observation-backed testimony about a subject is an INFORM voice — the 10.7 two-witness FOLD stays as-is above it; ECHO-DEDUP — near-identical ballot/turn rationales across distinct voters collapse to ONE voice so the 9B's homogeneity (audit H-4: 163 echo pairs) cannot fake independence)
- agents/memory/beliefs.py (the pre-vote INFORM: a single observation-backed witness moves every living listener's view of the subject by +0.05 PRE-VOTE — REUSE the 9.8 accusation unit, NO new constant — deduped once per meeting per subject; a baseline listener at 0.50 + inform = 0.55 stays UNDER the 0.60 gate (informs, never ejects alone); a listener at ≥0.55 prior crosses (corroboration). The teammate guard applies. The pre-vote inform REPLACES that subject-meeting's post-vote single-accuser bump — never double-counts)
- meetings/manager.py (apply the inform in the existing pre-vote fold half alongside the two-witness fold; vote prompts render AFTER, so §4.6 reads post-inform values; the EQUAL tally + tie→SKIP is UNCHANGED)
- tests/meetings/test_transcript.py + tests/agents/test_beliefs.py + tests/meetings/test_manager.py
- (no eval change required; the gp-7 metrics already read post-fold rendered values)

**Files NOT in scope:**
- the TALLY (NO reweight — equal votes + tie→SKIP stay frozen; V3 skip-halfweight is explicitly NOT implemented per the owner decision)
- the §4.6 render/threshold, the 9.8 constants (the +0.05 unit is reused, not re-tuned; decay untouched)
- the two-witness fold's existing behavior (the inform is ADDITIVE below it — single-voice was previously post-vote-only)
- the impostor toolkit, engine/orchestrator, replays/samples/**

**Definition of done:**
- [ ] Single-witness inform pin: one observation-backed relevance-passing witness moves every living listener +0.05 pre-vote, once; a BASELINE listener (0.50 prior) does NOT cross 0.60 on the inform alone (the anti-single-signal tripwire); a NEAR-GATE listener (≥0.55 prior) crosses.
- [ ] Bare-accusation pin: a verbal accusation with NO first-hand observation backing folds NOTHING (the seed-30-class pile-on still converts nothing — the owner-principle tripwire).
- [ ] Echo-dedup pin: N distinct voters emitting near-identical rationales collapse to ONE inform voice (audit's 163 echoes cannot manufacture independence).
- [ ] 37-bloc yield: offline re-derivation against the committed W1 bytes — count how many of the 37 over-gate-lost-plurality meetings the single-witness inform lifts a plurality of listeners over 0.60 in, converting WITHOUT any tally change (the deliverable number for the 10.17 expectation).
- [ ] Frozen-tally regression: the equal tally + tie→SKIP path is byte-unchanged; threshold_inversions stays 0 (the render reads post-inform values but the gate rule is untouched — a freshly-informed MUST-vote ballot is NOT an inversion).
- [ ] Determinism + full `bash scripts/check.sh` pass.

## Implementation hint

Reuse the 10.7 fold machinery and the 10.6 relevance predicate verbatim (one home) — the inform is
the single-witness extension of the two-witness fold, at the same +0.05, applied in the same pre-vote
half. The echo-dedup is the new guard and the H-4 fix; key it on normalized rationale text across
distinct speakers. The audit's per-voter rendered graphs (in the facts) show exactly which of the 37
meetings have near-gate listeners the inform would lift — that is the yield-pin oracle.

## Public types this task introduces
- `WITNESS_INFORM_REASON (or equivalent — the single-witness inform marker; name in the PR)`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Cascade is the risk this design exists to prevent; the +0.05 inform being strictly less than the
0.10 gate-distance from baseline is the structural guarantee that a single witness INFORMS but never
EJECTS a baseline listener — the baseline-listener pin is the tripwire wired to the owner principle.
The render-reads-post-fold seam must keep threshold_inversions at 0. Recording-side only.

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
Open a PR from branch `phase-10-belief-spread` with a title like `task 10.15: crew belief-spread lever (single-witness inform)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.2, §6.3, §4.6; audits/audit-2026-06-13-1816-gameplay-data.md C-C-1 + H-4; the owner belief-spread-first decision (2026-06-14); [[project_ejection_suspicion_principle]]), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
