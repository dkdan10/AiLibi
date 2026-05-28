# Agent Prompt — 5.1 Eval report schema (with format versioning)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 5.1 — Eval report schema (with format versioning), anchored to DESIGN.md §11.3, DESIGN.md §11.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-5-eval-report-schema`
**Depends on:** 4.16 merged, 4.17 merged
**Section refs:** DESIGN.md §11.3, DESIGN.md §11.4
**Complexity:** Small

Define the typed tournament/eval report schema in `eval/report_schema.py`.
This is the Phase 5 hub: every metric module (Tasks 5.2–5.5), the tournament
integration (Task 5.6), the dashboard (Task 5.7), and the regression suite
(Task 5.8) consume this one schema instead of scraping raw replay JSONL ad
hoc (DESIGN.md §11.3). It is the contract those six tasks build against, so
its field names and nesting are load-bearing — get them stable here.

The data this report must carry already exists as typed replay records
written per game during Phase 3/4 (DESIGN.md §11.4):

- `orchestrator.replay.GameEndReplayEntry` — decisive winner + reason per game.
- `orchestrator.replay.MeetingReplayEntry` — per meeting: `transcript`
  (`MeetingTranscript`), `ballots` (`tuple[VoteBallot, ...]`),
  `contradictions` (`tuple[ContradictionRef, ...]`), `outcome`
  (`MeetingOutcome`), `ejected_player_id`, `llm_calls`
  (`tuple[LLMCallRecord, ...]`), and `prompt_versions` (`Mapping[str, str]`).
- `orchestrator.replay.LLMCallRecord` — per call: `model`, `input_tokens`,
  `output_tokens`, `cost_usd`, `agent_id`, `call_kind`.
- `eval.balance_eval.BalanceReport` — current tournament-level outcome buckets
  (a frozen dataclass; see the BalanceReport decision below).

So 5.1 is largely an **aggregation + typing** task, not a from-scratch data
model: define a per-tournament Pydantic v2 artifact that composes these
existing per-game records into one typed object that downstream code reads
without re-parsing JSONL. Reuse the leaf meeting artifact types from
`meetings.schemas` (`MeetingTranscript`, `VoteBallot`, `ContradictionRef`,
`MeetingOutcome`, `PlayerId`) by import — do NOT redefine them. The `eval/`
package may import `meetings/`, `orchestrator/`, `engine/`, and `llm/`
freely; only `agents/` is firewalled from `engine/`, and this task touches
neither side of that boundary.

The schema carries a top-level `format_version: int` (carryover from Phase
4's deferred replay-format-versioning item) so future schema evolution is
explicit rather than relying on Pydantic's default-on-missing backward
compatibility. This task defines and versions the schema only. It does NOT
wire `scripts/run_tournament.py` to emit it and does NOT migrate
`run_balance_eval`'s return type — that integration is Task 5.6, which holds
`eval/balance_eval.py` and `scripts/run_tournament.py` in its scope.

**Files in scope:**
- eval/report_schema.py
- orchestrator/replay.py (add a `format_version` field to the replay entry models ONLY if the implementing agent resolves the format-version-namespace decision toward a shared namespace; the documented bias is report-only, which leaves replay.py untouched)
- tests/eval/test_report_schema.py

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/ (import its schemas; do not modify them)
- api/
- frontend/
- eval/balance_eval.py (BalanceReport migration is Task 5.6)
- eval/vote_correctness.py
- eval/accusation_calibration.py
- eval/alibi_fabrication.py
- eval/cost_dashboard.py
- eval/meeting_quality.py
- scripts/run_tournament.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `eval/report_schema.py` defines a top-level tournament report model (Pydantic v2) that composes, per game: the decisive outcome/winner, a reference to the game's replay file, the per-meeting artifacts (transcript, ballots, contradictions, outcome, ejected player), the per-call LLM cost/usage/model metadata, and the prompt-template versions in play. These are the structured inputs Phase 5 metrics consume; the report does NOT itself compute metric outputs.
- [ ] Leaf meeting artifact types (`MeetingTranscript`, `VoteBallot`, `ContradictionRef`, `MeetingOutcome`, `PlayerId`) are imported from `meetings.schemas`, not redefined.
- [ ] The top-level model carries a `format_version: int` field whose current value is `1`. A Pydantic field validator rejects any value greater than the current version (an unknown future format) with a clear error; a value less than current is accepted only if a documented migration path exists — for v1 there is no prior version, so only `1` is valid.
- [ ] The schema is structured so Phase 5 metric outputs can be attached by downstream tooling (Task 5.6) WITHOUT changing the raw per-game replay records — i.e. metrics compose over the report, they do not mutate replay JSONL.
- [ ] All models are `extra="forbid"` and frozen, consistent with `orchestrator.replay` and `meetings.schemas` conventions.
- [ ] Decision recorded in the PR's `## Decisions` block: whether `format_version` is namespaced to the report only (bias) OR shared across report + replay JSONL records. If shared, the replay entry models in `orchestrator/replay.py` gain the field; if report-only, `replay.py` is untouched. State which and why.
- [ ] Decision recorded in the PR's `## Decisions` block: the relationship between the new Pydantic report schema and the existing `eval.balance_eval.BalanceReport` dataclass. The bias is that the Pydantic report supersedes `BalanceReport` as the typed tournament artifact (Pydantic is the project convention for cross-module DTOs per AGENTS.md), with the actual `run_balance_eval` migration deferred to Task 5.6. Confirm the report can represent everything `BalanceReport` does (outcome buckets, seeds used) so 5.6 can drop the dataclass without information loss. Do NOT edit `balance_eval.py` in this task.
- [ ] `tests/eval/test_report_schema.py` covers: round-trip serialize/deserialize of a fully populated report; the `format_version` validator accepting `1` and rejecting `2`; `extra="forbid"` rejecting an unknown field; and a report built from a realistic multi-game / multi-meeting fixture.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes (firewall preserved).
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Public types this task introduces
- `eval.report_schema.TournamentReport`
- `eval.report_schema.GameReport`
- `eval.report_schema.MeetingReport`
- `eval.report_schema.GameCostSummary`
- `eval.report_schema.CURRENT_FORMAT_VERSION`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.replay.ReplayLog"`
- `uv run python -c "import api.schemas.BeliefEntryView"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.main"`

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
Open a PR from branch `phase-5-eval-report-schema` with a title like `task 5.1: eval report schema (with format versioning)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.3, DESIGN.md §11.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
