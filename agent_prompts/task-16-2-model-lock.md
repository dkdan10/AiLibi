# Agent Prompt — 16.2 The model lock: owner decision + the conditional-wave surgery

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.2 — The model lock: owner decision + the conditional-wave surgery, anchored to agent_prompts/task-14-6-lock-decision.md (the LOCKED-DECISION shape); tasks/phase-15.md 15.18 (the pause precedent for phase-doc surgery + prompt regeneration); scripts/validate_task_docs.py + scripts/generate_prompts.py (the tooling the surgery must keep green). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-model-lock`
**Depends on:** 16.1
**Section refs:** agent_prompts/task-14-6-lock-decision.md (the LOCKED-DECISION shape); tasks/phase-15.md 15.18 (the pause precedent for phase-doc surgery + prompt regeneration); scripts/validate_task_docs.py + scripts/generate_prompts.py (the tooling the surgery must keep green)
**Complexity:** Medium

The mid-phase owner gate. Consume 16.1's committed evidence and record the GO/NO-GO in
`audits/audit-phase-16-model-lock.md` (the 14.6 LOCKED-DECISION shape: the exact served model id,
thinking policy, `response_format_mode` posture, parse/latency evidence, the rejected path's
rationale — including "not served on the flat-rate plan" if that is the finding). Then perform the
phase-doc surgery this file's banner promises: under **GO**, concretize the Wave-2 contracts
(16.12–16.14 stay as written; fill the exact served id where this document says Qwen3.6-27b) and
confirm 16.15/16.16's template paths point at `agents/strategic/prompts/qwen3_6_27b/`; under
**NO-GO**, REMOVE the 16.12–16.14 contracts and their generated prompts entirely, replacing the
three with ONE prose drop record carrying the rationale (removal, not labeling:
`scripts/compute_next_task.py` computes dispatchability from `### Task` headers + merged PRs and
has no dropped state — a surviving header would surface forever as dispatchable), then rewrite
BOTH downstream prompt tasks: 16.15 (`Depends on:` drops 16.14; template paths to
`agents/strategic/prompts/qwen3_32b/`; bump arithmetic per-template — the three v5 templates → v6,
`vote_ballot` v6 → v7) and 16.16 (paths likewise to `qwen3_32b/`; its SECOND bump per-template —
the three → v7, `vote_ballot` → v8 — a set-level relabel would mint colliding stamps), and adjust
16.17's BEFORE column to baseline 3 plus the DAG/critical-path text. Either way: regenerate
`agent_prompts/`, keep the validator green, and update this file's STATUS banner to record the
lock outcome.

**Files in scope:**
- audits/audit-phase-16-model-lock.md (new: the decision record)
- tasks/phase-16.md (the conditional-wave surgery + banner line — this file)
- agent_prompts/ (mechanically regenerated task-16-* prompts — generator output, never hand-edited)

**Files NOT in scope:**
- llm/ + agents/strategic/prompts/ + scripts/ (no code or template change — the decision record and the doc surgery only; 16.12/16.13 implement)
- audits/ other than the new lock audit
- replays/ (untouched)

**Definition of done:**
- [ ] The lock audit records the decision in the 14.6 shape with every quoted number traced to `results-featherless-sweep-qwen3-6-27b.jsonl`, the exact served id (GO) or the NO-GO reason, and owner sign-off (the owner merges this PR — the 15.18 convention).
- [ ] The phase doc reflects the decision: GO → Wave 2 active with the served id concretized; NO-GO → the 16.12–16.14 contracts AND their prompts are REMOVED (one prose drop record remains; task/prompt counts fall by three, validator + `--check` green at the new counts, and `compute_next_task.py --phase 16` no longer lists them), 16.15 AND 16.16 rewritten (edges, paths, per-template arithmetic — 16.15: three v5 → v6, `vote_ballot` v6 → v7; 16.16's second bump: three → v7, `vote_ballot` → v8), 16.17's BEFORE column re-anchored to baseline 3, and the DAG/critical-path text updated.
- [ ] `uv run python scripts/validate_task_docs.py` and `uv run python scripts/generate_prompts.py --check` pass on the re-authored doc (the full-file validation discipline: a malformed phase doc breaks the repo's validator for every phase).
- [ ] The STATUS banner names the lock outcome and the date.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The surgery is textual but validator-bound: after every edit run the validator + `--check` locally
before committing (the 7-line tail is your own gate). The decision itself is the owner's — this
task's agent prepares the audit from the sweep evidence and presents both branches; the owner's
merge IS the sign-off. Keep the surgery minimal: contracts not named in the decision do not change.

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
Open a PR from branch `phase-16-model-lock` with a title like `task 16.2: the model lock: owner decision + the conditional-wave surgery`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing agent_prompts/task-14-6-lock-decision.md (the LOCKED-DECISION shape); tasks/phase-15.md 15.18 (the pause precedent for phase-doc surgery + prompt regeneration); scripts/validate_task_docs.py + scripts/generate_prompts.py (the tooling the surgery must keep green)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
