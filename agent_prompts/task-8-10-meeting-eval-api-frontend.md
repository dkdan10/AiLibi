# Agent Prompt — 8.10 Meeting eval-metric re-pointing + api meeting DTOs + frontend

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.10 — Meeting eval-metric re-pointing + api meeting DTOs + frontend, anchored to DESIGN.md §11.3 (eval metrics), §5.2; audits/restructure-impact-map-2026-06-04-0223.md §2b, §2f, §4 couplings 9 & 10. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-meeting-eval-api-frontend`
**Depends on:** 8.7, 8.4
**Section refs:** DESIGN.md §11.3 (eval metrics), §5.2; audits/restructure-impact-map-2026-06-04-0223.md §2b, §2f, §4 couplings 9 & 10
**Complexity:** Integration

Re-point everything that READS the meeting transcript to the chain `turns` shape (8.7): the four §11.3 metrics, the api meeting DTOs + loader views, and the frontend meeting render. `eval/vote_correctness.py` reads `transcript.reports[*].observations` (found_body + saw_player — if these silently vanish, evidence-backed ejections read as zero), `eval/accusation_calibration.py` walks `reports[*].claims` + `statements[*].claims`, `eval/alibi_fabrication.py` resolves the author from `ReportDocument.agent_id` + `Statement.speaker` — all re-point to iterate `transcript.turns` filtered by `turn_kind`/`observations`/`claims`/`speaker`. `api/schemas.py` (`StatementView`/`ReportView`/`MeetingView`) + `api/replay_loader.py` (`_statement_view`/`_report_view`/`_meeting_view`) + the shared `tests/api/fixtures/sample_replay.py` builder + the frontend meeting components move to the turn shape. This task also owns the `tests/api/test_leak.py` snapshot tripwires (both the per-player-task fields from 8.4 and the meeting-turn fields), updated in lockstep. The `tests/api/fixtures/sample_replay.py` builder hand-constructs the meeting record with **stubbed** `prompt_versions` (it does not consume 8.8's `DEFAULT_PROMPT_VERSIONS`), so 8.10 depends only on 8.7's schema + 8.4's task fields — not on 8.8.

**Files in scope:**
- eval/vote_correctness.py + eval/accusation_calibration.py + eval/alibi_fabrication.py (re-point the transcript readers to `turns`; preserve the observation/claim/author reads)
- eval/report_schema.py (`MeetingReport.transcript` flows the new `MeetingTranscript`)
- api/schemas.py (`StatementView` → turn view; `ReportView`/`MeetingView` reshaped to the turn list) + api/replay_loader.py (`_statement_view`/`_report_view`/`_meeting_view`/`_classify_template_id`)
- api/routes/replays.py + api/routes/eval.py (response models + the `TournamentEvalReport`/`MeetingReport` mirror)
- frontend/src/types/api.ts + frontend/src/components/MeetingView.tsx + StatementCard.tsx + ReportCard.tsx + ContradictionBadge.tsx + ThoughtStream.tsx + frontend/src/store/replayStore.ts (group by chain turn-order, not rounds)
- tests/api/fixtures/sample_replay.py (the shared meeting-replay builder → the turn record) + tests/eval/test_{vote_correctness,accusation_calibration,alibi_fabrication,report_schema,tournament_report}.py + tests/api/test_{schemas,replays,eval_routes}.py
- tests/api/test_leak.py (`EXPECTED_DTOS` + `EXPECTED_EVAL_REPORT_FIELDS` updated for the per-player-task fields (8.4) AND the turn fields; `test_eval_report_surface_exposes_no_engine_state_field` still passes)

**Files NOT in scope:**
- meetings/ (8.7), agents/strategic/ (8.8), tests/llm/ (8.9)
- eval/meeting_quality.py (`compute_meeting_rate` is meeting-granularity, not turn — re-baseline its expectations in 8.12, not here)

**Definition of done:**
- [ ] The four §11.3 metrics iterate `transcript.turns` and still read the observations (found_body/saw_player for the kill-witness chain), the accusation claims, and the author — `vote_correctness` evidence-backed ejections are NOT silently zeroed by a moved field.
- [ ] `api/schemas.py` meeting DTOs + `api/replay_loader.py` views + `frontend/src/types/api.ts` + the meeting components render the chain turn-order (no "Round N" grouping); the api↔frontend mirror stays 1:1 (`tsc`).
- [ ] The shared `tests/api/fixtures/sample_replay.py` builder constructs the turn record; the dependent api/eval suites are updated.
- [ ] `tests/api/test_leak.py`'s `EXPECTED_DTOS` + `EXPECTED_EVAL_REPORT_FIELDS` are updated for both the per-player-task fields and the turn fields (the deliberate tripwire), and `test_eval_report_surface_exposes_no_engine_state_field` still passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally (incl. frontend `tsc:check` + build).

## Implementation hint

Lock 8.7's `MeetingTranscript` first, then re-point. The risk metric is `vote_correctness` — its kill-witness chain reads `reports[*].observations`; ensure the opening turn's observations are where it looks. Mirror any new field through `eval/report_schema.py` → `api/routes/eval.py` → `frontend/src/types/api.ts` exactly as Task 7.3/7.11 did, and update the `test_leak.py` snapshot in the SAME PR (it depends on 8.4's task fields, hence the 8.4 dependency). The `sample_replay.py` builder fans out to several suites — update it once, centrally.

## Integration risk

This is the meeting reshape's largest reader surface and it owns the leak snapshot tripwires for BOTH the task-model and meeting changes — they must update in lockstep or a leaked field slips in silently. The api↔frontend mirror + `tsc` is a separate gate from pytest. A moved observation field silently zeroing `vote_correctness` is the subtle failure to test against.

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
Open a PR from branch `phase-8-meeting-eval-api-frontend` with a title like `task 8.10: meeting eval-metric re-pointing + api meeting dtos + frontend`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.3 (eval metrics), §5.2; audits/restructure-impact-map-2026-06-04-0223.md §2b, §2f, §4 couplings 9 & 10), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
