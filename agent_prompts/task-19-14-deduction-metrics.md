# Agent Prompt — 19.14 The deduction metrics: what "deduction" means, instrumented

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.14 — The deduction metrics: what "deduction" means, instrumented, anchored to audits/audit-phase-19-triage.md §7 item 15 [S-Codex/S-Claude convergent objective; §8 rows 3, 10, 14; the roll-call split and the 13-redirected-ejects cells are source-specific and NOT independently re-run — verify-then-fix] + item 24 disclosure twin (19.8); the headline cross-tab under its TWO distinct partitions, both pinned separately — MEETING-flag (9p2i samples: 70 flagged meetings → 68 imp/2 inn ejected, 95 unflagged → 10 imp/21 inn; unflagged-meeting accuracy 10/31 = 32.3%) and EJECTEE-specific-proof (68/101 ejections proof-present; accuracy among the 33 without ejectee-specific proof 10/33 = 30.3%; corpus twin 35/89 = 39.3%) — the fourth Codex round caught the two denominators being mixed in one sentence, which is exactly the C5 define-before-counting lesson; tests/eval/test_kill_craft.py:66-135 (the witnessed-supply pins to adopt). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-deduction-metrics`
**Depends on:** 19.5, 19.11, 19.18 (the last is the eval/meeting_quality.py serialization edge — labels land before the wrapper extension)
**Section refs:** audits/audit-phase-19-triage.md §7 item 15 [S-Codex/S-Claude convergent objective; §8 rows 3, 10, 14; the roll-call split and the 13-redirected-ejects cells are source-specific and NOT independently re-run — verify-then-fix] + item 24 disclosure twin (19.8); the headline cross-tab under its TWO distinct partitions, both pinned separately — MEETING-flag (9p2i samples: 70 flagged meetings → 68 imp/2 inn ejected, 95 unflagged → 10 imp/21 inn; unflagged-meeting accuracy 10/31 = 32.3%) and EJECTEE-specific-proof (68/101 ejections proof-present; accuracy among the 33 without ejectee-specific proof 10/33 = 30.3%; corpus twin 35/89 = 39.3%) — the fourth Codex round caught the two denominators being mixed in one sentence, which is exactly the C5 define-before-counting lesson; tests/eval/test_kill_craft.py:66-135 (the witnessed-supply pins to adopt)
**Complexity:** Medium

The precondition for any future gameplay phase (locked decision 6): make "deduction"
measurable without touching gameplay. One pure eval module computing, per set:
direct-proof vs non-direct ejection accuracy (the audits' cross-tab as a permanent,
pinned metric); weak-flag-only conviction rate; same-agent turn→ballot consistency;
public response coverage split by role; engine-redirected ballot share; witnessed and
co-present evidence supply (adopting the kill-craft cells); and scaffold-leakage rates
split between model-originated role/machinery statements and guard-originated stale
rationales — with each metric DEFINED in the module docstring before it is counted (the
C5 lesson: the audits' fourth-wall counts differed only by definition). The flag
classification must agree with 19.11's DTO taxonomy (cross-pinned counts on the same
bytes). Wire the headline cells into the report assembly and a proof-vs-inference
dashboard panel; regenerate the four derived reports. This module's committed cells are
the evidence the 19.28 close puts in front of the owner.

**Files in scope:**
- eval/deduction_metrics.py (new)
- tests/eval/test_deduction_metrics.py (new)
- scripts/build_sample_report.py; (report wiring)
- eval/meeting_quality.py; (ONLY the persisted `TournamentEvalReport` wrapper/assembler extension — the report model is `extra="forbid"`, so the new cells must be real fields on the canonical owner; no metric logic moves here)
- api/schemas.py; (the new report cells' DTO surface — additive)
- frontend/src/types/api.ts; (regenerated)
- frontend/src/components/TournamentDashboard.tsx; (the proof-vs-inference panel)
- frontend/src/stories/TournamentDashboard.stories.tsx; (the typed `baseReport()` fixture gains the deduction block)
- tests/api/test_leak.py; (the field-set snapshot updates again for the deduction block)
- api/routes/eval.py; (the `_TournamentEvalReportView` mirror gains the new top-level deduction block — `extra="forbid"` rejects it otherwise and `/eval/tournament-report` raises)
- replays/samples/4p1i/tournament-eval-report.json; (regenerated)
- replays/samples/9p2i/tournament-eval-report.json; (regenerated)
- replays/ml_corpus/4p1i/tournament-eval-report.json; (regenerated)
- replays/ml_corpus/9p2i/tournament-eval-report.json; (regenerated)
- tests/eval/test_report_schema.py; (the added cells)
- tests/eval/test_tournament_report.py

**Files NOT in scope:**
- meetings/ + agents/ (measurement only — zero substrate movement)
- eval/vote_correctness.py (consumed, not edited; 19.5 already landed its truth pass)
- eval/kill_craft.py (its cells are imported/adopted, not reimplemented)

**Definition of done:**
- [ ] Verify-then-fix for the source-specific cells: the roll-call coverage split and the engine-redirected eject count are recomputed from committed bytes before pinning (and the recount is the pin).
- [ ] The 9p2i cross-tab pins reproduce the triage's independent recount exactly UNDER BOTH PARTITIONS, each with its own named cell (meeting-flag: 70 flagged → 68/2, 95 unflagged → 10/21, unflagged accuracy 10/31; ejectee-proof: 68 proof-present, non-direct accuracy 10/33) — the module docstring defines both and no cell ever mixes their denominators; the corpus twins are pinned beside them.
- [ ] Every metric has a docstring definition stating numerator, denominator, and what it does NOT measure; the weak/proof classification counts match 19.11's DTO taxonomy on the same bytes (cross-pin).
- [ ] The regenerated reports carry the cells; the dashboard panel renders direct-proof vs non-direct accuracy side by side with honest labels; regeneration commands recorded.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Follow the `eval/deception_instruments.py` shape (pure function over the assembled report
+ replay records, one frozen report model, committed-bytes pins primary, Wilson intervals
on rare cells). The redirect markers and guard markers are greppable in recorded ballots;
the roll-call fields are in the recorded meeting records. Turn→ballot consistency needs a
definition that tolerates SKIP (an accusation followed by a SKIP ballot is inconsistency
only when the accused was votable) — write the definition first, then count.

## Public types this task introduces
- `eval.deduction_metrics.DeductionMetricsReport`
- `eval.deduction_metrics.compute_deduction_metrics`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
Open a PR from branch `phase-19-deduction-metrics` with a title like `task 19.14: the deduction metrics: what "deduction" means, instrumented`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 15 [S-Codex/S-Claude convergent objective; §8 rows 3, 10, 14; the roll-call split and the 13-redirected-ejects cells are source-specific and NOT independently re-run — verify-then-fix] + item 24 disclosure twin (19.8); the headline cross-tab under its TWO distinct partitions, both pinned separately — MEETING-flag (9p2i samples: 70 flagged meetings → 68 imp/2 inn ejected, 95 unflagged → 10 imp/21 inn; unflagged-meeting accuracy 10/31 = 32.3%) and EJECTEE-specific-proof (68/101 ejections proof-present; accuracy among the 33 without ejectee-specific proof 10/33 = 30.3%; corpus twin 35/89 = 39.3%) — the fourth Codex round caught the two denominators being mixed in one sentence, which is exactly the C5 define-before-counting lesson; tests/eval/test_kill_craft.py:66-135 (the witnessed-supply pins to adopt)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
