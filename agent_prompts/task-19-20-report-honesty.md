# Agent Prompt — 19.20 ML report honesty: paired statistics + terminology errata

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.20 — ML report honesty: paired statistics + terminology errata, anchored to audits/audit-phase-19-triage.md §7 item 20 [S-Codex/S-Claude; §8 row 4 VERIFIED exactly] + C2 + C9; training/reports/report-finalist-eval.md (the paired-stats erratum target; :115-118 + :1066-1070 the external-slate citations); training/reports/results-finalist-eval.jsonl (the recomputation base — the triage's exact McNemar: ea4bc955 17/4 p=0.0072; bfd145cb 20/5 p=0.0041; 6d327dcb 15/9 p=0.3075 n.s.; 7f73929d 12/3@n=49 p=0.0352, fails Bonferroni α=0.0125); report-conviction-model.md:196 (0.9375 = conversion-label) + report-composed-runner.md:120-159 (0.8646/0.7917); report-impostor-campaign.md:415-465 (the screening instability + late-measured instrument noise); the 19.4 reward-claim erratum. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-report-honesty`
**Depends on:** 19.4
**Section refs:** audits/audit-phase-19-triage.md §7 item 20 [S-Codex/S-Claude; §8 row 4 VERIFIED exactly] + C2 + C9; training/reports/report-finalist-eval.md (the paired-stats erratum target; :115-118 + :1066-1070 the external-slate citations); training/reports/results-finalist-eval.jsonl (the recomputation base — the triage's exact McNemar: ea4bc955 17/4 p=0.0072; bfd145cb 20/5 p=0.0041; 6d327dcb 15/9 p=0.3075 n.s.; 7f73929d 12/3@n=49 p=0.0352, fails Bonferroni α=0.0125); report-conviction-model.md:196 (0.9375 = conversion-label) + report-composed-runner.md:120-159 (0.8646/0.7917); report-impostor-campaign.md:415-465 (the screening instability + late-measured instrument noise); the 19.4 reward-claim erratum
**Complexity:** Medium

The reports are records — they get additive, dated errata, never rewrites. Land: (a) a
paired-statistics erratum in the finalist report — the exact McNemar table recomputed
from the committed per-game rows, stating plainly that the SHIPPED champion's paired edge
is statistically unresolved at n=50 and one arm fails the multiplicity correction; (b)
terminology errata wherever 0.9375 is called decision accuracy (the composed 0.8646 is
the decision figure); (c) the reward-shaping erratum (19.4's finding, with the
uncausal-as-measured statement about evidence starvation); (d) a screening-instability
note quoting the report's own late-discovery admission, framed as a stopping-rule
lesson; (e) a retained-findings note keeping N1/N2 and the clean negatives quotable. The
recomputation lives in `scripts/paired_stats.py` (exact binomial McNemar + Wilson) with
tests — 19.23 consumes it.

**Files in scope:**
- training/reports/report-finalist-eval.md; (additive dated erratum)
- training/reports/report-conviction-model.md; (same)
- training/reports/report-composed-runner.md; (same)
- training/reports/report-impostor-campaign.md; (same)
- training/reports/report-ballot-surrogate.md; (same, where the decision channel is described)
- scripts/paired_stats.py (new)
- tests/scripts/test_paired_stats.py (new)

**Files NOT in scope:**
- training/reports/results-finalist-eval.jsonl (the evidence rows are read, never edited)
- README.md (19.1 already carries the front-door terminology fix)

**Definition of done:**
- [ ] `scripts/paired_stats.py` recomputes the four McNemar cells from the committed JSONL exactly matching the triage's §8 row 4 values (pinned), plus Wilson intervals; the erratum quotes the recomputation command.
- [ ] Every erratum is additive and dated, never an in-place rewrite; each names what it corrects and quotes the original.
- [ ] The n.s. shipped-champion statement and the Bonferroni failure are stated in the finalist erratum in plain language.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Exact McNemar: two-sided binomial test on the discordant pair (min(b,c), b+c, p=0.5) —
pure stdlib via `math.comb`. Follow the repo's existing errata idiom (the crew report's
§12 errata are the exemplar: numbered, dated, each quoting the sentence it corrects).

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
Open a PR from branch `phase-19-report-honesty` with a title like `task 19.20: ml report honesty: paired statistics + terminology errata`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 20 [S-Codex/S-Claude; §8 row 4 VERIFIED exactly] + C2 + C9; training/reports/report-finalist-eval.md (the paired-stats erratum target; :115-118 + :1066-1070 the external-slate citations); training/reports/results-finalist-eval.jsonl (the recomputation base — the triage's exact McNemar: ea4bc955 17/4 p=0.0072; bfd145cb 20/5 p=0.0041; 6d327dcb 15/9 p=0.3075 n.s.; 7f73929d 12/3@n=49 p=0.0352, fails Bonferroni α=0.0125); report-conviction-model.md:196 (0.9375 = conversion-label) + report-composed-runner.md:120-159 (0.8646/0.7917); report-impostor-campaign.md:415-465 (the screening instability + late-measured instrument noise); the 19.4 reward-claim erratum), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
