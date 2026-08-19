# Agent Prompt — 17.5 Vent-placement widening: the mechanism (inert) + the double-count counterfactual

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 17.5 — Vent-placement widening: the mechanism (inert) + the double-count counterfactual, anchored to audits/audit-phase-16-close.md §0.1.4 + §8 (the PR #264 question, routed WITH the absence decision); meetings/transcript.py:1205 `absent_players` + `reconstruct_stated_paths` (the placement substrate — `saw_player` observations only, by contract); the 15.4 vent-grounding chokepoint (grounded vent sightings — the only class that may place); tests/agents/test_absence_prior.py `TestAbsencePriorOnCommittedBytes` (the counterfactual harness the new column extends). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-17.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-17-vent-placement-widening`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-16-close.md §0.1.4 + §8 (the PR #264 question, routed WITH the absence decision); meetings/transcript.py:1205 `absent_players` + `reconstruct_stated_paths` (the placement substrate — `saw_player` observations only, by contract); the 15.4 vent-grounding chokepoint (grounded vent sightings — the only class that may place); tests/agents/test_absence_prior.py `TestAbsencePriorOnCommittedBytes` (the counterfactual harness the new column extends)
**Complexity:** Medium

Build what the gate needs and nothing the substrate would feel: (1) an
`include_vent_sightings` flag on the absent-set derivation — a GROUNDED vent sighting
(matched against the speaker's own `VentWitnessRecord`, the 15.4 chokepoint; spoken but
ungrounded claims never place) removes its subject from the absent set; the flag
defaults OFF and NOTHING in production passes it, so every committed byte and every
stated-path contradiction read is untouched. (2) The double-count counterfactual on
committed baseline-5 bytes: how many meetings hold a vent-sighted subject who is ALSO
absent (the population the widening would re-place), and the absent-set size / new-over-
gate / top-churn deltas with the widening hypothetically applied — the missing evidence
row the 17.7 gate reads beside 17.4's uptake breakdown.

**Files in scope:**
- meetings/transcript.py (the `include_vent_sightings` parameter on the absent-set derivation — the stated-paths reconstruction itself is untouched)
- tests/meetings/test_absent_set.py (flag semantics: grounded places, ungrounded never; default-OFF byte-identity)
- tests/agents/test_absence_prior.py (the counterfactual extension — the widened column beside the existing pinned walk)

**Files NOT in scope:**
- meetings/manager.py + agents/memory/beliefs.py (no live consumer passes the flag — the gate rules first)
- `_detect_alibi_vs_physical` and every contradiction detector (byte-preserving by contract — the flag-minting variant is routed, never done here)

**Definition of done:**
- [ ] Flag OFF (the default and the only production state) is byte-identical everywhere: no call site passes it, committed reconstruction and golden stay green, and the absent-set derivation's existing pins are unmoved.
- [ ] Flag ON semantics fixture-pinned: a grounded vent sighting places its subject (removed from the absent set); an ungrounded spoken vent claim places nobody; a grounded sighting of an already-placed subject changes nothing.
- [ ] The double-count counterfactual on committed baseline-5 9p2i bytes is pinned: the vent-sighted∩absent population per meeting, and the widened-column deltas (absent-set sizes, new-over-gate count, top-churn count) beside the existing counterfactual's cells — the gate's evidence row, quoted in the PR description.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The grounding predicate exists — reuse the 15.4/16.7 chokepoint logic (the vent accessor
+ witness-record match), never a fresh text parse. Keep the flag on the DERIVATION
(`absent_players` or its input assembly), not on `reconstruct_stated_paths` itself: the
stated-paths surface is the alibi-contradiction substrate and must not learn vents.

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
Open a PR from branch `phase-17-vent-placement-widening` with a title like `task 17.5: vent-placement widening: the mechanism (inert) + the double-count counterfactual`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-16-close.md §0.1.4 + §8 (the PR #264 question, routed WITH the absence decision); meetings/transcript.py:1205 `absent_players` + `reconstruct_stated_paths` (the placement substrate — `saw_player` observations only, by contract); the 15.4 vent-grounding chokepoint (grounded vent sightings — the only class that may place); tests/agents/test_absence_prior.py `TestAbsencePriorOnCommittedBytes` (the counterfactual harness the new column extends)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
