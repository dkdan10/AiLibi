# Agent Prompt — 18.1 Tier-A deception instruments: false-vouch, frame jobs, teammate immunity

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.1 — Tier-A deception instruments: false-vouch, frame jobs, teammate immunity, anchored to audits/audit-phase-18-planning.md §3.1–§3.2 (the census: 455 frame attempts, 34 false vouches, 5 conversions; the gap table); eval/funnel.py `_vouch_census` (:1404) + `_grounded_vouch_set` (:1430); eval/alibi_fabrication.py:153 (the survival analyzer to adopt); eval/meeting_quality.py:2277 (`EffectiveDeflectionReport`, the role-agnostic neighbor). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-deception-instruments`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §3.1–§3.2 (the census: 455 frame attempts, 34 false vouches, 5 conversions; the gap table); eval/funnel.py `_vouch_census` (:1404) + `_grounded_vouch_set` (:1430); eval/alibi_fabrication.py:153 (the survival analyzer to adopt); eval/meeting_quality.py:2277 (`EffectiveDeflectionReport`, the role-agnostic neighbor)
**Complexity:** Medium

The deception behaviors the phase targets already exist in the committed bytes and are
un-instrumented. Build the Tier-A analyzer set as one pure module over `TournamentReport`:
**false-vouch rate** (impostor turns whose `SawPlayerObservation`/`CorroborationClaim`
subject is the co-impostor; grounded-vs-fabricated split via the production
`grounded_vouch_subjects` chokepoint), **frame-attempt and frame-conversion rate** (impostor
`AccusationClaim` against a true crewmate; conversion = that crewmate ejected — rare-event,
reported with the advisory discipline), **teammate-non-accusation index** (0/455 on the
corpus today), and adoption wrappers surfacing the existing fabricated-alibi survival and
deflection-efficacy analyzers beside them. Every cell population-relative in framing; every
committed-bytes value pinned (corpus + samples denominators).

**Files in scope:**
- eval/deception_instruments.py (new)
- tests/eval/test_deception_instruments.py (committed-bytes pins + synthetic fixtures)

**Files NOT in scope:**
- eval/funnel.py + eval/alibi_fabrication.py + eval/meeting_quality.py (consumed, never edited)
- eval/watchability.py; (no floor changes — these are diagnostics, not gates)

**Definition of done:**
- [ ] On the committed corpus bytes the module reports the census cells (impostor→crew accusations, teammate accusations 0, false vouches, frame conversions) with numerators/denominators pinned; the grounded-vs-fabricated vouch split runs through the production grounding chokepoint, never a re-derivation.
- [ ] Rare-event cells (frame conversions ≤ 7 numerator) carry the advisory label and a Wilson interval beside the point estimate, per the 15.19 rare-event rule.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Follow the `eval/alibi_fabrication.py` shape: a pure function over the assembled report +
roles, one frozen Pydantic report model, committed-bytes pins as the primary tests. The
vouch census and subject-membership patterns you need already exist (`eval/funnel.py:1404`,
`eval/alibi_fabrication.py:219`) — reuse their logic via import where public, otherwise
mirror with a comment naming the source.

## Public types this task introduces
- `eval.deception_instruments.DeceptionInstrumentsReport`
- `eval.deception_instruments.compute_deception_instruments`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-18-deception-instruments` with a title like `task 18.1: tier-a deception instruments: false-vouch, frame jobs, teammate immunity`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §3.1–§3.2 (the census: 455 frame attempts, 34 false vouches, 5 conversions; the gap table); eval/funnel.py `_vouch_census` (:1404) + `_grounded_vouch_set` (:1430); eval/alibi_fabrication.py:153 (the survival analyzer to adopt); eval/meeting_quality.py:2277 (`EffectiveDeflectionReport`, the role-agnostic neighbor)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
