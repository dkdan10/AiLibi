# Agent Prompt — 18.4 THE EMERGENCE PRE-REGISTRATION (owner)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.4 — THE EMERGENCE PRE-REGISTRATION (owner), anchored to audits/audit-phase-18-planning.md §5 (the operationalization + the four-part claim discipline); the 18.1/18.2/18.3 committed pins (the baseline cells); audits/audit-phase-17-close.md §3 (the corpus-denominator anchor discipline this memo inherits). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-emergence-preregistration`
**Depends on:** 18.1, 18.2, 18.3
**Section refs:** audits/audit-phase-18-planning.md §5 (the operationalization + the four-part claim discipline); the 18.1/18.2/18.3 committed pins (the baseline cells); audits/audit-phase-17-close.md §3 (the corpus-denominator anchor discipline this memo inherits)
**Complexity:** Medium

The memo that makes "emergence" falsifiable before anything trains. Author
`audits/audit-phase-18-emergence-preregistration.md`: for each pre-registered instrument
(Tier A: false-vouch, frame attempt/conversion, teammate immunity, fabricated-alibi
survival, deflection efficacy; Tier B: kill-timing vs witness density, off-menu rate,
action entropy), quote the committed baseline cell with its denominator, and register the
claim discipline: a behavior counts as EMERGENT only if (a) its instrument delta vs the
same-seed scripted-FSM comparator on the real path is significant at |z| ≥ 1.96 on the
pre-registered denominator; (b) the delta reproduces across at least 2 of the 3 corpus
seed-splits; (c) a named counterfactual ablation (remove the enabling lever/feature) shows
the behavior recede; (d) the behavior is selected-for — present in the champion's
recordings, not only the archive. Watchability improvement is never itself an emergence
claim. The owner ratifies bars and instrument list by merge; amendments are recorded in the
memo, and 18.27 reads against this memo verbatim.

**Files in scope:**
- audits/audit-phase-18-emergence-preregistration.md (new: the memo + the ratified bars)

**Files NOT in scope:**
- eval/ (no instrument changes at pre-registration; defects found here route back as contracts)
- tasks/phase-18.md (no surgery at this gate)

**Definition of done:**
- [ ] Every pre-registered instrument's baseline cell is quoted from a committed test pin or committed report with its source named; no hand-computed figures.
- [ ] The four-part claim discipline is stated with the exact statistical rule (pooled two-proportion z for rates; the split-reproducibility rule; the ablation naming convention) and the owner's ratification is recorded verbatim.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The 17.7 gate shape: evidence first, decision slots explicit, bars proposed with both
directions priced. Rare-event cells (frame conversions at n=5) get advisory framing — the
memo must say what denominator would power them and whether the phase expects to reach it.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.off_menu"`
- `uv run python -c "import eval.kill_craft"`
- `uv run python -c "import eval.deception_instruments"`

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
Open a PR from branch `phase-18-emergence-preregistration` with a title like `task 18.4: the emergence pre-registration (owner)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §5 (the operationalization + the four-part claim discipline); the 18.1/18.2/18.3 committed pins (the baseline cells); audits/audit-phase-17-close.md §3 (the corpus-denominator anchor discipline this memo inherits)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
