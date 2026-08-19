# Agent Prompt — 19.11 The evidence taxonomy: proof is not a contradiction

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.11 — The evidence taxonomy: proof is not a contradiction, anchored to audits/audit-phase-19-triage.md §7 item 12 [S-Codex/S-Claude; §8 rows 10, 14] + item 20 (the four mechanisms preserved as separate fixtures); meetings/schemas.py:442-456 (vent_sighting: "both event ids reference the SAME spoken observation"); meetings/transcript.py:2857-2917 (the self-linked emission; `event_a_id = event_b_id` at :2909-2910); frontend/src/components/MeetingView.tsx:303-385 with :348 (every flag rendered `A ↔ B`, so grounded vent proof shows as `p-X ↔ p-X` under "Contradictions"); the traced injustice exhibits (§8 row 14: seed 17 M0, seed 47; plus seed 12 M0, seed 23 M1, 4p1i seeds 41/49). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-evidence-taxonomy`
**Depends on:** 19.10
**Section refs:** audits/audit-phase-19-triage.md §7 item 12 [S-Codex/S-Claude; §8 rows 10, 14] + item 20 (the four mechanisms preserved as separate fixtures); meetings/schemas.py:442-456 (vent_sighting: "both event ids reference the SAME spoken observation"); meetings/transcript.py:2857-2917 (the self-linked emission; `event_a_id = event_b_id` at :2909-2910); frontend/src/components/MeetingView.tsx:303-385 with :348 (every flag rendered `A ↔ B`, so grounded vent proof shows as `p-X ↔ p-X` under "Contradictions"); the traced injustice exhibits (§8 row 14: seed 17 M0, seed 47; plus seed 12 M0, seed 23 M1, 4p1i seeds 41/49)
**Complexity:** Integration

A grounded vent sighting is role proof, not a contradiction — but the schema carries it
through `ContradictionRef` and the UI renders `p-1 ↔ p-1` under "Contradictions", while
weak interval flags render with the same visual weight as hard proof. Derive an evidence
taxonomy at the DTO layer (recorded bytes and `meetings/` schemas are frozen — this is
classification, not schema migration): every flag classifies as ROLE-PROOF (vent_sighting
/ self-linked), CROSS-STATEMENT CONTRADICTION, or WEAK-SIGNAL (the `[weak signal…]`
description stamp), fail-loud on anything unclassifiable. The UI renders proof as proof
(no self-linked `↔`), subordinates weak flags visually, and never labels an unverified
statement-pair "VERIFIED". Preserve the four evidence-honesty mechanisms as SEPARATE
committed fixtures so the post-19 decision has executable exhibits: the
provenance-impossible sighting (9p2i seed 23 M1), the content-vs-own-memory miss (seed 12
M0), the one-tick interval artifact (4p1i seeds 41/49), and the equal-weight conflict
(seed 41). Prompt templates are NOT touched (locked decision 1) — the prompt-side flag
naming routes to the post-19 decision.

**Files in scope:**
- api/schemas.py
- api/replay_loader.py
- frontend/src/types/api.ts; (regenerated)
- frontend/src/types/api.fidelity.ts; (regenerated — both generator artifacts)
- frontend/src/components/MeetingView.tsx
- frontend/src/components/TurnCard.tsx; (the INLINE evidence renderer — `ContradictionMarker` branches on `severity` alone at :100-105/:261-316, so a self-linked vent proof still renders contradiction-styled inline; the marker branches on the category)
- frontend/src/stories/MeetingView.stories.tsx; (`CHAIN_CONTRADICTIONS` constructs `ContradictionView` literals — the category field lands in the fixture or tsc fails)
- frontend/src/stories/MindInspector.stories.tsx; (same — `CONTRADICTION` at :89)
- frontend/src/components/ContradictionBadge.tsx; (the MindInspector's evidence badge styles by `kind` alone — it receives the full DTO, so it branches on the category here; MindInspector itself passes the flag through untouched and stays 19.12's file)
- frontend/src/components/BallotCard.tsx; (the guard-chip visibility gate — `teammate_coerced` arrives as data in `ballot.rewrite_reasons` via replay_loader:2437 and renders unconditionally at :105-114, disclosing the impostor pairing outside omniscient view)
- tests/api/

**Files NOT in scope:**
- meetings/schemas.py + meetings/transcript.py (recorded-byte schemas and emission are frozen; the taxonomy derives)
- agents/strategic/prompts/ (substrate behavior — the NOT-list)
- eval/ (the eval-side twin of this classification is 19.14's)

**Definition of done:**
- [ ] The classification is total over all committed bytes: a pin counts each category corpus-wide (samples + ml_corpus) and an unknown kind fails loud, never defaults.
- [ ] The committed self-linked vent records render as role proof (no `p-X ↔ p-X` anywhere); weak-stamped flags are visually subordinated; the four mechanism fixtures exist with their seed/meeting anchors and one-line descriptions of what each demonstrates.
- [ ] Role-disclosing guard chips (`teammate_coerced` in `rewrite_reasons`) render in OMNISCIENT perspective ONLY — never under as-agent fog, regardless of the outcome-reveal state (reveal governs outcome information, perspective governs current-frame knowledge, per the playback task's own semantics; a revealed outcome must not expose the impostor pairing through fog). Fixture-pinned in as-agent view under BOTH reveal states, plus the omniscient case.
- [ ] The DTO change is additive; older fixtures parse; the fidelity fixture regenerates green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The classifier is one pure function over the flag record (kind, event ids, description
stamps) living API-side; keep it in one place with the category rules readable as a
table. `event_a_id == event_b_id` or `kind == "vent_sighting"` ⇒ role proof; the
`[weak signal` stamp is already machine-detectable in `description`. 19.14 implements the
eval-side twin — the two classifications are cross-pinned (same counts on the same
bytes), which is why the category rules must be trivially portable.

## Public types this task introduces
- `api.schemas.EvidenceCategory`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

The taxonomy touches the most-watched UI surface and a served DTO in one PR. Two guards:
the corpus-wide category-count pin (any classification drift is a loud diff), and
additive-only DTO fields so no existing consumer breaks. If any committed flag defies the
three categories, stop and record it as a finding — never add a silent OTHER bucket.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.schemas"`

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

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-19-evidence-taxonomy` with a title like `task 19.11: the evidence taxonomy: proof is not a contradiction`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 12 [S-Codex/S-Claude; §8 rows 10, 14] + item 20 (the four mechanisms preserved as separate fixtures); meetings/schemas.py:442-456 (vent_sighting: "both event ids reference the SAME spoken observation"); meetings/transcript.py:2857-2917 (the self-linked emission; `event_a_id = event_b_id` at :2909-2910); frontend/src/components/MeetingView.tsx:303-385 with :348 (every flag rendered `A ↔ B`, so grounded vent proof shows as `p-X ↔ p-X` under "Contradictions"); the traced injustice exhibits (§8 row 14: seed 17 M0, seed 47; plus seed 12 M0, seed 23 M1, 4p1i seeds 41/49)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
