# Agent Prompt — 19.5 Metric and data-display truth: the conversion family and the dashboard

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.5 — Metric and data-display truth: the conversion family and the dashboard, anchored to audits/audit-phase-19-triage.md §7 items 5+6 [S-Claude; §8 rows 7, 8; the alibi 0.0-vs-None row was UNVERIFIED in the triage and is now re-verified at HEAD: eval/alibi_fabrication.py:88-94]; eval/meeting_quality.py:618-624 ("Expected ~0 … bug to chase") — CORRECTED PREMISE: the partition ALREADY imports `UNCITED_ZERO_FLAG_EJECT_MARKER` (eval/meeting_quality.py:179, censused as `citation_coerced_skip_ballots`), and the committed 9p2i report carries `citation_coerced_skip_ballots = 1` BESIDE `threshold_inversions = 87` — so the 87 are NOT unrecognized citation-gated SKIPs (the triage C6 mechanism is refuted; the three-surface doctrine disagreement stands); frontend/src/components/TournamentDashboard.tsx:296-312 (the "gate bug — expect 0" badge), :327-344 (the starved `genuine_class_conversion` labeled "PRIMARY gate"), :423-426 (the survival_rate n/a special case); eval/vote_correctness.py:11-25 (the sentinel demotion the dashboard ignores), :676-688 (`supplied_channel_conversion` — "the ONLY canary-eligible genuine-class cell"); scripts/measure_baseline.py (zero canary references — grep-verified). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-metric-display-truth`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-19-triage.md §7 items 5+6 [S-Claude; §8 rows 7, 8; the alibi 0.0-vs-None row was UNVERIFIED in the triage and is now re-verified at HEAD: eval/alibi_fabrication.py:88-94]; eval/meeting_quality.py:618-624 ("Expected ~0 … bug to chase") — CORRECTED PREMISE: the partition ALREADY imports `UNCITED_ZERO_FLAG_EJECT_MARKER` (eval/meeting_quality.py:179, censused as `citation_coerced_skip_ballots`), and the committed 9p2i report carries `citation_coerced_skip_ballots = 1` BESIDE `threshold_inversions = 87` — so the 87 are NOT unrecognized citation-gated SKIPs (the triage C6 mechanism is refuted; the three-surface doctrine disagreement stands); frontend/src/components/TournamentDashboard.tsx:296-312 (the "gate bug — expect 0" badge), :327-344 (the starved `genuine_class_conversion` labeled "PRIMARY gate"), :423-426 (the survival_rate n/a special case); eval/vote_correctness.py:11-25 (the sentinel demotion the dashboard ignores), :676-688 (`supplied_channel_conversion` — "the ONLY canary-eligible genuine-class cell"); scripts/measure_baseline.py (zero canary references — grep-verified)
**Complexity:** Medium

Three surfaces disagree about whether the flagship dashboard displays a bug, the declared
canary metric is wired to nothing, and two tiles mislead by name. Fix the family in one
pass: (a) the threshold-inversions re-doctrine, RECOUNT FIRST: the partition already
consumes the citation-gate marker (see Section refs — the corrected premise), so the
committed 87 inversions have an unmeasured cause mix; recount them by cause from
committed bytes (the partition's own inputs), record the by-cause table as a pinned
fixture, and THEN rewrite `eval/meeting_quality.py`'s "Expected ~0 … bug" prose and the
dashboard badge to the post-13.13 doctrine (nonzero intended) with whatever named split
the recount actually supports — never a cell invented ahead of the count; (b) wire
`supplied_channel_conversion` into the report assembly and `measure_baseline` output, and
demote the starved `genuine_class_conversion` tile to an explicitly historical label;
(c) rename/re-explain the `vote_correctness_rate` tile as what it is (evidence-backed
share of impostor ejections — a sentinel, not overall correctness); (d) make undefined
`alibi_fabrication.survival_rate` follow the package's None-iff-undefined convention and
delete the frontend special case that papers over it. Regenerate the four committed
`tournament-eval-report.json` derived views from committed replay bytes ($0) and update
the affected pins, quoting each delta in the PR. Replay bytes never move.

**Files in scope:**
- eval/meeting_quality.py
- eval/vote_correctness.py
- eval/alibi_fabrication.py
- eval/prompt_regression.py; (the None convention propagates — `alibi_survival_rate` is consumed at :257 into a required `float` at :161, so the regression metrics model widens with it)
- tests/eval/test_prompt_regression.py
- tests/api/test_leak.py; (`EXPECTED_EVAL_REPORT_FIELDS` is an exact field-set snapshot — the canary cell's addition updates the reviewed pin)
- tests/eval/test_gate_metrics.py; (24 complete `GateMetricsReport` literals gain the new sibling field or the gate fails)
- tests/scripts/test_measure_baseline_cli.py; (the exact CLI contract pins the new canary in both the report and CLI output cases — otherwise a silent omission stays green)
- api/routes/eval.py; (only if the mirrored `_TournamentEvalReportView` chain surfaces the new nested cell — its `extra="forbid"` revalidation must accept the regenerated report; record whether an edit was needed)
- scripts/measure_baseline.py
- scripts/build_sample_report.py; (the report-assembly wiring for the canary cell)
- api/schemas.py; (the report-DTO surface the new/None-able cells flow through — additive)
- frontend/src/types/api.ts; (regenerated)
- frontend/src/components/TournamentDashboard.tsx
- frontend/src/stories/TournamentDashboard.stories.tsx; (its `baseReport()` constructs the typed report explicitly — new required fields must land in the fixture or tsc fails)
- replays/samples/4p1i/tournament-eval-report.json; (regenerated derived view)
- replays/samples/9p2i/tournament-eval-report.json; (regenerated derived view)
- replays/ml_corpus/4p1i/tournament-eval-report.json; (regenerated derived view)
- replays/ml_corpus/9p2i/tournament-eval-report.json; (regenerated derived view)
- tests/eval/test_meeting_quality.py
- tests/eval/test_vote_correctness.py
- tests/eval/test_alibi_fabrication.py
- tests/eval/test_report_schema.py
- tests/eval/test_tournament_report.py

**Files NOT in scope:**
- meetings/manager.py (the marker constant is imported, never edited)
- eval/watchability.py (floors and referee untouched — no gate moves)
- replays/**/replay-seed-*.jsonl (recorded bytes are frozen)

**Definition of done:**
- [ ] Verify-then-fix for the one previously-unverified element: confirm the 0.0-vs-None behavior at `eval/alibi_fabrication.py:88-94` before changing it (it is re-verified at HEAD; re-run the check in-session and quote it).
- [ ] The recount of the committed 87 inversions is recorded (a by-cause table in the PR + a pinned fixture over committed bytes); the partition's docstring and the dashboard badge state the post-13.13 doctrine consistent with the recount; any bucket split ships only if the recount supports it; the existing marker consumption (`meeting_quality.py:179` ← `meetings.manager`) is pinned as already-wired, not re-derived.
- [ ] `supplied_channel_conversion` appears in the regenerated reports and in `measure_baseline` output; the dashboard's gate tile shows it; the starved cell is labeled historical; the correctness tile is renamed/explained; the alibi tile renders n/a from a true `None`; the dashboard's rubric histogram section (:452-541) carries the narrow internal-heuristic label (19.9's labeling rule, applied here because this task owns the file).
- [ ] Every regenerated view is byte-reproducible from committed replays with the exact command recorded in the PR; `bash scripts/verify_samples.sh` stays green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Land the eval-side reclassification first and regenerate reports once, at the end, so the
pin churn happens in one commit. The dashboard consumes generated types — if a report cell
is added, extend `api`/report schema surfaces the reports actually flow through (follow
`scripts/build_sample_report.py`'s existing assembly; `tests/eval/test_report_schema.py`
shows the shape contract). The frontend n/a special case to delete sits at
`TournamentDashboard.tsx:423-426`.

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
Open a PR from branch `phase-19-metric-display-truth` with a title like `task 19.5: metric and data-display truth: the conversion family and the dashboard`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 items 5+6 [S-Claude; §8 rows 7, 8; the alibi 0.0-vs-None row was UNVERIFIED in the triage and is now re-verified at HEAD: eval/alibi_fabrication.py:88-94]; eval/meeting_quality.py:618-624 ("Expected ~0 … bug to chase") — CORRECTED PREMISE: the partition ALREADY imports `UNCITED_ZERO_FLAG_EJECT_MARKER` (eval/meeting_quality.py:179, censused as `citation_coerced_skip_ballots`), and the committed 9p2i report carries `citation_coerced_skip_ballots = 1` BESIDE `threshold_inversions = 87` — so the 87 are NOT unrecognized citation-gated SKIPs (the triage C6 mechanism is refuted; the three-surface doctrine disagreement stands); frontend/src/components/TournamentDashboard.tsx:296-312 (the "gate bug — expect 0" badge), :327-344 (the starved `genuine_class_conversion` labeled "PRIMARY gate"), :423-426 (the survival_rate n/a special case); eval/vote_correctness.py:11-25 (the sentinel demotion the dashboard ignores), :676-688 (`supplied_channel_conversion` — "the ONLY canary-eligible genuine-class cell"); scripts/measure_baseline.py (zero canary references — grep-verified)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
