# Agent Prompt — 17.7 THE ABSENCE GATE: graduation + vent-widening ruling (owner) + phase-doc surgery

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 17.7 — THE ABSENCE GATE: graduation + vent-widening ruling (owner) + phase-doc surgery, anchored to audits/audit-phase-16-close.md §0.1.4 (the stay-OFF ruling this gate re-opens, its evidence bar, and the coupled PR #264 question); tests/agents/test_absence_prior.py (the baseline-5 counterfactual: 53/179 new-over-gate, 114/179 top-churn + 17.5's widened column); eval/funnel.py (17.4's uptake breakdown); tasks/phase-15.md 15.18 + tasks/phase-16.md 16.2 (the gate-with-surgery precedents). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-17.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-17-absence-gate`
**Depends on:** 17.4, 17.5
**Section refs:** audits/audit-phase-16-close.md §0.1.4 (the stay-OFF ruling this gate re-opens, its evidence bar, and the coupled PR #264 question); tests/agents/test_absence_prior.py (the baseline-5 counterfactual: 53/179 new-over-gate, 114/179 top-churn + 17.5's widened column); eval/funnel.py (17.4's uptake breakdown); tasks/phase-15.md 15.18 + tasks/phase-16.md 16.2 (the gate-with-surgery precedents)
**Complexity:** Medium

The phase's first owner gate, sequenced BEFORE the corpus record by locked decision 3.
Assemble the decision memo in `audits/audit-phase-17-absence-gate.md`: the baseline-5
counterfactual (already pinned), 17.4's who-is-not-answering breakdown, 17.5's
double-count counterfactual with the widened deltas, and a stated graduation bar the
owner ratifies or amends (the close never defined one — this memo must propose a
numeric bar, e.g. a new-over-gate ceiling at a stated roll-call coverage, so the ruling
is a criterion, not a vibe). The owner rules THREE couplings together: graduate/stay-OFF,
ship/hold the vent widening (a widening that ships travels WITH the graduation record —
it is meeting-layer), and (if stay-OFF) the Phase-18 routing note. Then the surgery,
exactly as the preamble's Baseline-numbering block enumerates: GO ⇒ 17.8 stays, 17.8
enters 17.9's `Depends on:` line (the parsed edge that makes the corpus wait), the
mover baseline renumbers 6 → 7 across 17.11/17.12/17.17, 17.17's before-column artifact
renames to `baseline6-final-measure.json`, and this doc's banner records the ruling;
STAY-OFF ⇒ 17.8's contract + prompt are REMOVED with the reason recorded (the 16.2
surgery discipline) and the GO-conditional 17.8 clauses in 17.9's DoD and 17.11's body
are scrubbed — dependencies and scopes otherwise untouched. Prompts regenerate;
validator green either way.

**Files in scope:**
- audits/audit-phase-17-absence-gate.md (new: the memo + the recorded ruling)
- tasks/phase-17.md (the surgery + the banner note)
- agent_prompts/ (regenerated)

**Files NOT in scope:**
- agents/memory/beliefs.py + orchestrator/replay.py (graduation mechanics are 17.8's, GO only)
- replays/samples/ (no record at the gate)

**Definition of done:**
- [ ] The memo quotes every evidence row (counterfactual, uptake breakdown, widening deltas) with its committed source, proposes the numeric bar, and records the owner's three rulings verbatim (graduate/stay-OFF; widening ship/hold; routing).
- [ ] The surgery is complete in the ruled direction: validator green, prompts regenerated, `scripts/compute_next_task.py --phase 17` consistent with the surviving DAG; under STAY-OFF no orphan reference to 17.8 survives anywhere in tasks/ or agent_prompts/.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Write the memo BEFORE asking for the ruling (the 15.18 pause shape: evidence first,
decision slots explicit). The bar proposal should price both directions honestly — the
lever's designed value (pricing refusal-to-account) against the quiet-crewmate cost at
the measured uptake, and what the widening buys (17.5's delta) toward shrinking the
absent set.

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
Open a PR from branch `phase-17-absence-gate` with a title like `task 17.7: the absence gate: graduation + vent-widening ruling (owner) + phase-doc surgery`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-16-close.md §0.1.4 (the stay-OFF ruling this gate re-opens, its evidence bar, and the coupled PR #264 question); tests/agents/test_absence_prior.py (the baseline-5 counterfactual: 53/179 new-over-gate, 114/179 top-churn + 17.5's widened column); eval/funnel.py (17.4's uptake breakdown); tasks/phase-15.md 15.18 + tasks/phase-16.md 16.2 (the gate-with-surgery precedents)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
