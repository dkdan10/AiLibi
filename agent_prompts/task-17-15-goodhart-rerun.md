# Agent Prompt — 17.15 The Goodhart probe re-run on the re-grounded surrogate

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 17.15 — The Goodhart probe re-run on the re-grounded surrogate, anchored to tasks/phase-15.md 15.14 (the probe design); training/bakeoff/goodhart.py (the probe machinery + the baseline delta anchor 17.11 re-measured); training/reports/report-goodhart-probe.md (regenerated). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-17.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-17-goodhart-rerun`
**Depends on:** 17.10, 17.11
**Section refs:** tasks/phase-15.md 15.14 (the probe design); training/bakeoff/goodhart.py (the probe machinery + the baseline delta anchor 17.11 re-measured); training/reports/report-goodhart-probe.md (regenerated)
**Complexity:** Medium

Re-run the reward-hacking probe against the re-grounded surrogate: can an optimizer
exploit surrogate-vs-real divergence on the baseline-5 economy? The Phase-15 reading
(bounded divergence, no exploitable seam at the measured scale) must be re-earned, not
assumed — the new economy has MORE structure in ballots (citations) that the 6-feature
surrogate cannot see, which is exactly where a gap could open. Regenerate the report
with the delta anchors from 17.11's re-measured baseline.

**Files in scope:**
- training/reports/report-goodhart-probe.md (regenerated)
- training/bakeoff/goodhart.py (probe-run wiring only if the protocol needs the new anchors threaded)
- tests/training/test_goodhart_probe.py (re-pins)

**Files NOT in scope:**
- training/surrogate/ (consumes 17.10's artifact)
- training/bakeoff/harness.py (17.12's)

**Definition of done:**
- [ ] The probe re-runs end-to-end on the re-grounded surrogate with the re-measured anchors; the report states the divergence reading and whether the Phase-15 no-exploitable-seam conclusion survives baseline 5, with the citation-blindness caveat addressed explicitly.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The probe is an instrument, not a gate — a widened divergence is a finding that bounds
how hard 17.12's optimizers may lean on the surrogate (the max-uses budget already
prices this); say the implication, don't re-plan the bake-off.

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
Open a PR from branch `phase-17-goodhart-rerun` with a title like `task 17.15: the goodhart probe re-run on the re-grounded surrogate`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-15.md 15.14 (the probe design); training/bakeoff/goodhart.py (the probe machinery + the baseline delta anchor 17.11 re-measured); training/reports/report-goodhart-probe.md (regenerated)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
