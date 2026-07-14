# Agent Prompt — 17.11 Selection-bar re-pins: the bake-off flips to the baseline-5 floors

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 17.11 — Selection-bar re-pins: the bake-off flips to the baseline-5 floors, anchored to training/bakeoff/harness.py:114 `CORPUS_SPLITS_PATH` + :125 `BAKEOFF_BASELINE_ID` + :165 `GOODHART_9P2I_BASELINE` (the three baseline-3 anchors); eval/watchability.py:799 `_DEFAULT_BASELINE_ID` (already baseline-5 — the note at :795 says the bake-off constant lags deliberately until this task); training/crew/scorer.py (imports the constant); training/bakeoff/goodhart.py (the default baseline_id). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-17.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-17-selection-bar-repins`
**Depends on:** 17.9
**Section refs:** training/bakeoff/harness.py:114 `CORPUS_SPLITS_PATH` + :125 `BAKEOFF_BASELINE_ID` + :165 `GOODHART_9P2I_BASELINE` (the three baseline-3 anchors); eval/watchability.py:799 `_DEFAULT_BASELINE_ID` (already baseline-5 — the note at :795 says the bake-off constant lags deliberately until this task); training/crew/scorer.py (imports the constant); training/bakeoff/goodhart.py (the default baseline_id)
**Complexity:** Small

Flip the training-side selection anchors to the close-era floors: `BAKEOFF_BASELINE_ID`
→ `"baseline-5"` (the literal pinned by the 17.7 STAY-OFF ruling), the goodhart
default with it, and re-measure `GOODHART_9P2I_BASELINE`'s
fake-provider probe numbers at the current tree ($0, offline). `CORPUS_SPLITS_PATH`
stays put — 17.9 regenerated its file in place. Re-pin the training tests that read
these constants. After this task, every candidate the harness scores is judged against
the floors the phase selects on.

**Files in scope:**
- training/bakeoff/harness.py (the two constants + the probe re-measure)
- training/bakeoff/goodhart.py (the default)
- training/crew/scorer.py (only if the import shape needs the explicit id)
- eval/watchability.py (the :794-798 lag note ONLY — the note says the bake-off constant deliberately lags until Phase 17; this task closes it. Floor BLOCKS stay record-pinned and are not touched)
- tests/training/test_bakeoff_harness.py + test_goodhart_probe.py (constant + probe re-pins)

**Files NOT in scope:**
- eval/watchability.py floor blocks (floors are pinned by records — 17.17 — never by this task; only the :794-798 note region above is in scope)
- training/surrogate/ (17.10)

**Definition of done:**
- [ ] Both constants name the selection baseline; the watchability note at eval/watchability.py:795-798 is updated to say the lag is closed; no test or module still selects baseline-3 floors on the training side (grepped, stated in the PR).
- [ ] `GOODHART_9P2I_BASELINE` is re-measured at HEAD (the probe run quoted), never hand-copied.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

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
Open a PR from branch `phase-17-selection-bar-repins` with a title like `task 17.11: selection-bar re-pins: the bake-off flips to the baseline-5 floors`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing training/bakeoff/harness.py:114 `CORPUS_SPLITS_PATH` + :125 `BAKEOFF_BASELINE_ID` + :165 `GOODHART_9P2I_BASELINE` (the three baseline-3 anchors); eval/watchability.py:799 `_DEFAULT_BASELINE_ID` (already baseline-5 — the note at :795 says the bake-off constant lags deliberately until this task); training/crew/scorer.py (imports the constant); training/bakeoff/goodhart.py (the default baseline_id)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
