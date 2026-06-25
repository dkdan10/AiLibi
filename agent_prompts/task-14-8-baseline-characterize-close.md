# Agent Prompt — 14.8 Characterize the new baseline (R-gate as measurement) + phase close

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-14.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 14.8 — Characterize the new baseline (R-gate as measurement) + phase close, anchored to audits/audit-2026-06-25-0859-phase-13-close.md (the R-gate definition); tasks/phase-13.md (R1/R4/R7 + impostor win rate + rubric geomean); eval/meeting_quality.py; experiments/lab/rubric_score.py. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-14.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-14-baseline-characterize-close`
**Depends on:** 14.7
**Section refs:** audits/audit-2026-06-25-0859-phase-13-close.md (the R-gate definition); tasks/phase-13.md (R1/R4/R7 + impostor win rate + rubric geomean); eval/meeting_quality.py; experiments/lab/rubric_score.py
**Complexity:** Medium

Design-thread close: compute the Phase-13 R-gate as a MEASUREMENT over the committed 14.7 baseline — R1
(games decided by ejection), R4 floor, R7, impostor win rate, and the rubric geomean ranking (eject-decided >
stopwatch) — and compare to the final-9B baseline (R1 3/50, impostor 84%, eject 9%). Write the close audit
framing the result as an honest finding: state whether the stronger model raised R1 and, if not, whether the
evidence supports the information-ceiling hypothesis (single-room vision → ~45% detector precision → correct
SKIP), recommending Phase 15 (asymmetric visibility / information richness). This is characterization, not a
gate — the phase already merged on the valid new baseline (14.7); a flat or down R1 is a recorded finding.

**Files in scope:**
- audits/audit-2026-06-25-phase-14-close.md (new: the R-gate measurement + the hypothesis-test verdict + the Phase 15 recommendation)
- tasks/phase-14.md (a STATUS banner recording the R-gate outcome and the next step)
- experiments/lab/results-rubric-score.json (re-ranked offline over the new committed replays — data regen, no code change)
- experiments/lab/report-rubric-interestingness.md (re-ranked offline — data regen)

**Files NOT in scope:**
- llm/ + agents/ + meetings/ + engine/ (no behavior change at close)
- replays/samples/ (the 14.7 bytes are the baseline; close READS them)
- eval/ source (the analyzers are reused as-is; this folds, it does not change them)

**Definition of done:**
- [ ] The R-gate is computed offline over the 14.7 baseline (R1, R4 floor, R7, impostor win rate, rubric geomean ranking) and compared to the final-9B baseline (R1 3/50, impostor 84%, eject 9%).
- [ ] The close audit frames the verdict as an HONEST hypothesis test: it states whether the model raised R1, and if not, whether the evidence supports the information-ceiling hypothesis; a null result is recorded as a valid finding, never a blocker.
- [ ] The close audit recommends the next phase (asymmetric visibility / information richness if the ceiling is confirmed; prompt/tactical work if a gap remains).
- [ ] The rubric data is re-ranked offline over the new committed replays ($0, no code change); no number is retrofit to pass.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Pure offline folds over the new `TournamentReport`: `eval/vote_correctness.py` (`ejection_accuracy`,
`compute_genuine_class_conversion`), `eval/accusation_calibration.py` (ECE), `eval/alibi_fabrication.py`
(survival_rate), assembled by `eval/meeting_quality.py`, plus the rubric geomean from
`experiments/lab/rubric_score.py` — all $0, no provider. The framing is the deliverable: per the Phase-13
audit the bottleneck may be INFORMATION not the model, so "R1 did not rise even on a Qwen3-32B-class model" is
a genuine finding that redirects Phase 15, not a Phase-14 failure. Do not retrofit any number.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import llm.featherless_client"`
- `uv run python -c "import llm.provider"`

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
Open a PR from branch `phase-14-baseline-characterize-close` with a title like `task 14.8: characterize the new baseline (r-gate as measurement) + phase close`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-2026-06-25-0859-phase-13-close.md (the R-gate definition); tasks/phase-13.md (R1/R4/R7 + impostor win rate + rubric geomean); eval/meeting_quality.py; experiments/lab/rubric_score.py), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
