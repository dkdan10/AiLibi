# Agent Prompt — 19.4 The reward-invariance claim correction

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.4 — The reward-invariance claim correction, anchored to audits/audit-phase-19-triage.md §7 item 4 + singleton 1 [S-Codex; VERIFIED §8 row 2]; training/rewards.py:18-24 (the false "cannot change the optimal policy" claim), :82-102 (`_side_potential` = cumulative kills/tasks — trajectory-dependent terminal potential), :157-198 + :259-305 (the kill-term economy vs ±1 terminal); tests/training/test_rewards.py:153-168 (proves telescoping only). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-reward-claim`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-19-triage.md §7 item 4 + singleton 1 [S-Codex; VERIFIED §8 row 2]; training/rewards.py:18-24 (the false "cannot change the optimal policy" claim), :82-102 (`_side_potential` = cumulative kills/tasks — trajectory-dependent terminal potential), :157-198 + :259-305 (the kill-term economy vs ±1 terminal); tests/training/test_rewards.py:153-168 (proves telescoping only)
**Complexity:** Small

The shaping claim is mathematically false: at γ=1 the sum telescopes to
Φ(terminal)−Φ(initial), and because Φ(terminal) is cumulative kills it is
trajectory-dependent — the shaping is a real +1-per-kill incentive, not policy-invariant.
Correct the claim in code and pin the truth: a test with two trajectories of equal
environment reward and different terminal kill counts whose shaped returns differ. No
retraining, and no computed value moves — this changes prose and adds a test, nothing
else; the ML program is frozen and the finding is documented, not repaired. The
report-side erratum (recording the possible contribution to evidence-starved policies,
uncausal as measured) rides 19.20.

**Files in scope:**
- training/rewards.py; (docstring/comment lines only — computed values byte-identical)
- tests/training/test_rewards.py

**Files NOT in scope:**
- training/bakeoff/harness.py (the fitness consumer is untouched)
- training/reports/ (the erratum belongs to 19.20)

**Definition of done:**
- [ ] The docstring states the true property (telescoping ≠ invariance; the terminal-potential qualification) and names the +1/kill equivalence.
- [ ] The new test demonstrates non-invariance (two trajectories, equal env reward, different shaped return) and an existing-value pin proves no computed number moved.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

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
Open a PR from branch `phase-19-reward-claim` with a title like `task 19.4: the reward-invariance claim correction`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 4 + singleton 1 [S-Codex; VERIFIED §8 row 2]; training/rewards.py:18-24 (the false "cannot change the optimal policy" claim), :82-102 (`_side_potential` = cumulative kills/tasks — trajectory-dependent terminal potential), :157-198 + :259-305 (the kill-term economy vs ±1 terminal); tests/training/test_rewards.py:153-168 (proves telescoping only)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
