# Agent Prompt — 13.4 alibi_vs_physical STRONG from reconstructed testimony (B3/B4)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.4 — alibi_vs_physical STRONG from reconstructed testimony (B3/B4), anchored to experiments/lab/report-phase-b-plan.md (B3/B4); meetings/transcript.py (the 13.2 helper, `is_relevant_sighting`). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-strong-physical`
**Depends on:** 13.2, 13.3
**Section refs:** experiments/lab/report-phase-b-plan.md (B3/B4); meetings/transcript.py (the 13.2 helper, `is_relevant_sighting`)
**Complexity:** Integration
**Files in scope:**
- meetings/transcript.py
- tests/meetings/test_contradictions.py
**Files NOT in scope:**
- perception-time deltas — the firewall exposes no per-player liveness channel, so ALL absence/last-seen inference lives
  in the meeting layer over public testimony only
- agents/memory/beliefs.py (13.5); engine/ and recordings — NO re-record

Add a new `alibi_vs_physical` contradiction kind in `meetings/transcript.py`, emitted from the 13.2 reconstruction over
PUBLIC testimony: a subject whose stated alibi is physically impossible given other speakers' stated sightings, or who is
the last speaker-placed party with the victim before the body. Emit STRONG ONLY under a TWO-SOURCE conjunction (the
subject's uncorroborated claim AND an independent physical placement); a lone atom emits at the weak/mid band. DROP all
perception-time forms (no liveness channel exists). Reuse `is_relevant_sighting` + endpoint-tick exclusion.
**Definition of done:** new `alibi_vs_physical` STRONG flags are emitted from transcript reconstruction (public testimony
only — no engine/perception); RE-EXTRACT + `rubric_score.py` shows R7 climbs further with every STRONG flag role-gated to
a true impostor (STRONG-on-crewmate ≈ 0, gp-3 watch-the-games BLOCKING); an assertion test confirms no flag references a
placement not traceable to a transcript `saw_player`; a lone atom cannot reach the §4.6 gate alone (only the two-source
conjunction does); $0, NO re-record; `scripts/check.sh` is green.

## Implementation hint
consume the 13.2 helper (stated paths); STRONG only on the two-source conjunction, single atoms weak/mid; reuse
`is_relevant_sighting` + endpoint-tick exclusion; no perception-time delta (the firewall has no liveness channel).

## Integration risk
firewall — every placement MUST trace to a public `saw_player`; since a leak test does not scan the belief layer, the
"traceable-to-transcript" assertion test is the guard; STRONG-on-crewmate is a false positive (Goodhart R7 / R4) →
role-gate + count; two-source-only keeps a lone reconstruction atom from ejecting alone (the wrong-ejection path the weak
delta closed).

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
Open a PR from branch `phase-13-strong-physical` with a title like `task 13.4: alibi_vs_physical strong from reconstructed testimony (b3/b4)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing experiments/lab/report-phase-b-plan.md (B3/B4); meetings/transcript.py (the 13.2 helper, `is_relevant_sighting`)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
