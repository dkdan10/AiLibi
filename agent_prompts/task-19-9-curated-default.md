# Agent Prompt — 19.9 The curated spectator default + the featured path + the rubric re-score

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.9 — The curated spectator default + the featured path + the rubric re-score, anchored to audits/audit-phase-19-triage.md §7 item 10 [C; §8 rows 10, 16] + singleton 29; api/replay_loader.py:2653 (`DEFAULT_SET = "4p1i"`); frontend/src/components/ReplayPicker.tsx:19-20 + :211-213 (the false "mostly zero-meeting" copy — actual: 39/50 4p1i games have exactly one meeting, 11/50 zero), :284-290 (the staleness banner keyed on git_head); frontend/src/components/GuidedTour.tsx:30 (the tour already targets 9p2i best-rubric); experiments/lab/rubric_score.py (offline, $0 — verified: no LLM/provider imports); engine/maps/canonical_1.yaml:39-44 (the map's own "only crew win path becomes ejection" intent that 4p1i's task-timer economy contradicts); the audits' named good tail (9p2i seeds 2/8/17/23; 4p1i 41/29/2). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-curated-default`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-19-triage.md §7 item 10 [C; §8 rows 10, 16] + singleton 29; api/replay_loader.py:2653 (`DEFAULT_SET = "4p1i"`); frontend/src/components/ReplayPicker.tsx:19-20 + :211-213 (the false "mostly zero-meeting" copy — actual: 39/50 4p1i games have exactly one meeting, 11/50 zero), :284-290 (the staleness banner keyed on git_head); frontend/src/components/GuidedTour.tsx:30 (the tour already targets 9p2i best-rubric); experiments/lab/rubric_score.py (offline, $0 — verified: no LLM/provider imports); engine/maps/canonical_1.yaml:39-44 (the map's own "only crew win path becomes ejection" intent that 4p1i's task-timer economy contradicts); the audits' named good tail (9p2i seeds 2/8/17/23; 4p1i 41/29/2)
**Complexity:** Medium

The weakest set is the product default and its copy is false. Flip `DEFAULT_SET` to
`"9p2i"`; relabel 4p1i honestly ("fast technical fixture — median ~12 ticks, at most one
meeting, most games decided by the task timer"); replace the false picker copy with
recomputed facts; re-run the rubric scorer at HEAD to clear the staleness banner (a $0
offline regeneration of the committed derived view); and add a hand-curated FEATURED list
— the named good-tail seeds with a one-line why-watch label each. Curation is editorial
and by hand: a fresh rubric score clears staleness but does NOT validate human-interest
ordering, so wherever the rubric scalar renders it is labeled narrowly ("internal
pacing/structure heuristic — not a human rating").

**Files in scope:**
- api/replay_loader.py; (the DEFAULT_SET constant + the featured-list serving, if served)
- frontend/src/api/client.ts; (ONLY the omitted-set contract comment at :62-65 — it documents the 4p1i server default this task retires — plus a pin that an omitted `set` resolves 9p2i)
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/GuidedTour.tsx; (retarget onto the curated featured entry if its selection rule changes)
- replays/samples/9p2i/results-rubric-score.json; (regenerated at HEAD — derived view)
- tests/api/

**Files NOT in scope:**
- frontend/src/hooks/usePlayback.ts + frontend/src/App.tsx (19.10's files)
- experiments/lab/rubric_score.py (run, not edited)
- replays/**/replay-seed-*.jsonl (frozen)

**Definition of done:**
- [ ] The API default set is 9p2i (pinned in tests/api/), the client's omitted-set contract comment states it, and the picker's 4p1i copy quotes recomputed meeting-count facts with the fixture relabel.
- [ ] The rubric re-score is committed, the staleness banner is clear at HEAD, and the regeneration command is recorded in the PR.
- [ ] The featured list exists (the named seeds + editorial labels), the tour lands on a featured game, and the rubric scalar carries the narrow label on THE SURFACES THIS TASK OWNS (the picker); the other two rendering surfaces are labeled by their owning tasks — HighlightCard's score badge by 19.10 and the dashboard's rubric histogram by 19.5 (each carries a matching DoD line).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The featured list is data, not machinery: a small committed structure (seed, set, one-line
label) served beside the replay list — resist building a curation system. GuidedTour
already picks the rubric's best 9p2i game; after re-scoring, verify its target is on the
featured list and pin that agreement.

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
Open a PR from branch `phase-19-curated-default` with a title like `task 19.9: the curated spectator default + the featured path + the rubric re-score`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 10 [C; §8 rows 10, 16] + singleton 29; api/replay_loader.py:2653 (`DEFAULT_SET = "4p1i"`); frontend/src/components/ReplayPicker.tsx:19-20 + :211-213 (the false "mostly zero-meeting" copy — actual: 39/50 4p1i games have exactly one meeting, 11/50 zero), :284-290 (the staleness banner keyed on git_head); frontend/src/components/GuidedTour.tsx:30 (the tour already targets 9p2i best-rubric); experiments/lab/rubric_score.py (offline, $0 — verified: no LLM/provider imports); engine/maps/canonical_1.yaml:39-44 (the map's own "only crew win path becomes ejection" intent that 4p1i's task-timer economy contradicts); the audits' named good tail (9p2i seeds 2/8/17/23; 4p1i 41/29/2)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
