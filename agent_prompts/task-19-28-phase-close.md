# Agent Prompt — 19.28 The phase close (owner)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.28 — The phase close (owner), anchored to [L] the phase-18 close conventions (audits/audit-phase-18-close.md — the exemplar); locked decision 6 (the post-19 menu reads the 19.14 metrics); tasks/post-phase-14-plan.md (the roadmap tick this close owns). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-close`
**Depends on:** 19.8, 19.17, 19.23, 19.26, 19.27
**Section refs:** [L] the phase-18 close conventions (audits/audit-phase-18-close.md — the exemplar); locked decision 6 (the post-19 menu reads the 19.14 metrics); tasks/post-phase-14-plan.md (the roadmap tick this close owns)
**Complexity:** Medium

The close re-verifies and routes. `audits/audit-phase-19-close.md`: re-run the full gate,
`verify_samples`, and `verify_ml_evidence` at close HEAD; re-verify each contract's
headline DoD with fresh commands (merge equals done, but the close re-runs — the
phase-18 precedent found real defects in otherwise-green merges); the phase ledger
(every deviation recorded as a finding, never silently); the before/after story told in
generated numbers (gate runtime, clone weight, the truth-check counts). Then the routed
decision: the post-19 menu — the evidence-honesty substrate phase vs the presentation
phase — put to the owner with the 19.14 proof-vs-inference cells as the evidence (locked
decision 6), a costed recommendation, and no unilateral ruling. STATUS banner flips in
this file; the roadmap gets its tick.

**Files in scope:**
- audits/audit-phase-19-close.md (new)
- tasks/phase-19.md; (the STATUS banner + any close-recorded surgery notes)
- tasks/post-phase-14-plan.md; (the roadmap tick)
- docs/artifacts.md; (close-recorded surgery, 2026-08-18: the audits/ registry-count row ONLY — landing the close audit moves the fail-loud in-tree family inventory by one, so the close bumps the one counted cell; ratified by the merge of the close PR, the 15.18 convention)

**Files NOT in scope:**
- everything else (the close verifies; it does not fix — late findings route to the next phase's inputs)

**Definition of done:**
- [ ] The close's gate rerun is the WHOLE gate, not the default subset, invoked by the verifiers' ACTUAL paths: `bash scripts/check.sh` AND `uv run pytest -m campaign` (the 19.27 opt-in tier) AND `bash scripts/fetch_evidence.sh` followed by `uv run python scripts/verify_ml_evidence.py --complete` (every archived hash verified; a manifest-recorded LOST class accepted) AND `bash scripts/verify_samples.sh` — all green at close HEAD with outputs quoted; every contract is verified-or-deviation-recorded in the ledger.
- [ ] The post-19 decision menu is framed from the committed 19.14 cells with a recommendation; the owner's ruling is recorded in the close audit.
- [ ] The STATUS banner and roadmap reflect the close.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Follow the phase-18 close's section shape at a fraction of its length — this phase
recorded nothing, so the close is verification + routing, not evidence assembly. The
decision menu's framing rule: outcomes, risks, and costs per option, recommendation
first, the 19.14 numbers doing the arguing.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.replay_walk"`
- `uv run python -c "import eval.leak_scan"`
- `uv run python -c "import training.realpath_schema"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import api.schemas"`

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
Open a PR from branch `phase-19-close` with a title like `task 19.28: the phase close (owner)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing [L] the phase-18 close conventions (audits/audit-phase-18-close.md — the exemplar); locked decision 6 (the post-19 menu reads the 19.14 metrics); tasks/post-phase-14-plan.md (the roadmap tick this close owns)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
