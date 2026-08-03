# Agent Prompt — 19.5 Metric and data-display truth: the conversion family and the dashboard

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.5 — Metric and data-display truth: the conversion family and the dashboard, anchored to audits/audit-phase-19-triage.md §7 items 5+6 [S-Claude; §8 rows 7, 8; the alibi 0.0-vs-None row was UNVERIFIED in the triage and is now re-verified at HEAD: eval/alibi_fabrication.py:88-94]; eval/meeting_quality.py:618-624 ("Expected ~0 … bug to chase") vs meetings/manager.py:313-323 (`UNCITED_ZERO_FLAG_EJECT_MARKER` — "the partition must learn this literal"); the committed 9p2i report's `/conversion/threshold_inversions = 87`; frontend/src/components/TournamentDashboard.tsx:296-312 (the "gate bug — expect 0" badge), :327-344 (the starved `genuine_class_conversion` labeled "PRIMARY gate"), :423-426 (the survival_rate n/a special case); eval/vote_correctness.py:11-25 (the sentinel demotion the dashboard ignores), :676-688 (`supplied_channel_conversion` — "the ONLY canary-eligible genuine-class cell"); scripts/measure_baseline.py (zero canary references — grep-verified). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-metric-display-truth`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-19-triage.md §7 items 5+6 [S-Claude; §8 rows 7, 8; the alibi 0.0-vs-None row was UNVERIFIED in the triage and is now re-verified at HEAD: eval/alibi_fabrication.py:88-94]; eval/meeting_quality.py:618-624 ("Expected ~0 … bug to chase") vs meetings/manager.py:313-323 (`UNCITED_ZERO_FLAG_EJECT_MARKER` — "the partition must learn this literal"); the committed 9p2i report's `/conversion/threshold_inversions = 87`; frontend/src/components/TournamentDashboard.tsx:296-312 (the "gate bug — expect 0" badge), :327-344 (the starved `genuine_class_conversion` labeled "PRIMARY gate"), :423-426 (the survival_rate n/a special case); eval/vote_correctness.py:11-25 (the sentinel demotion the dashboard ignores), :676-688 (`supplied_channel_conversion` — "the ONLY canary-eligible genuine-class cell"); scripts/measure_baseline.py (zero canary references — grep-verified)
**Complexity:** Medium

Three surfaces disagree about whether the flagship dashboard displays a bug, the declared
canary metric is wired to nothing, and two tiles mislead by name. Fix the family in one
pass: (a) teach the conversion partition the `UNCITED_ZERO_FLAG_EJECT_MARKER` literal
(imported from `meetings.manager`, never re-derived) so citation-gated SKIPs are
classified instead of lumped into `threshold_inversions`, and re-doctrine
`eval/meeting_quality.py`'s prose plus the dashboard badge to the post-13.13 intent
(nonzero is expected; the bucket splits into named cells); (b) wire
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
- scripts/measure_baseline.py
- scripts/build_sample_report.py; (the report-assembly wiring for the canary cell)
- frontend/src/components/TournamentDashboard.tsx
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
- [ ] The regenerated 9p2i sample report classifies the former `threshold_inversions = 87` bucket into named cells with the marker-matched population separated; the partition's docstring and the dashboard badge state the post-13.13 doctrine; a fixture proves the marker literal is consumed from `meetings.manager`, not duplicated.
- [ ] `supplied_channel_conversion` appears in the regenerated reports and in `measure_baseline` output; the dashboard's gate tile shows it; the starved cell is labeled historical; the correctness tile is renamed/explained; the alibi tile renders n/a from a true `None`.
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
Open a PR from branch `phase-19-metric-display-truth` with a title like `task 19.5: metric and data-display truth: the conversion family and the dashboard`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 items 5+6 [S-Claude; §8 rows 7, 8; the alibi 0.0-vs-None row was UNVERIFIED in the triage and is now re-verified at HEAD: eval/alibi_fabrication.py:88-94]; eval/meeting_quality.py:618-624 ("Expected ~0 … bug to chase") vs meetings/manager.py:313-323 (`UNCITED_ZERO_FLAG_EJECT_MARKER` — "the partition must learn this literal"); the committed 9p2i report's `/conversion/threshold_inversions = 87`; frontend/src/components/TournamentDashboard.tsx:296-312 (the "gate bug — expect 0" badge), :327-344 (the starved `genuine_class_conversion` labeled "PRIMARY gate"), :423-426 (the survival_rate n/a special case); eval/vote_correctness.py:11-25 (the sentinel demotion the dashboard ignores), :676-688 (`supplied_channel_conversion` — "the ONLY canary-eligible genuine-class cell"); scripts/measure_baseline.py (zero canary references — grep-verified)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
