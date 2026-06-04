# Agent Prompt — 8.11 Replay/report versioning

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.11 — Replay/report versioning, anchored to DESIGN.md §11.4 (versioning); audits/restructure-impact-map-2026-06-04-0223.md §3.3, §5 decision 10. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-versioning`
**Depends on:** 8.1, 8.7, 8.10
**Section refs:** DESIGN.md §11.4 (versioning); audits/restructure-impact-map-2026-06-04-0223.md §3.3, §5 decision 10
**Complexity:** Medium

Apply decision 10. The replay JSONL stays **unversioned** — the per-tick `state_hash` (changed by 8.1) + the per-set `roster.json` already reject any old replay, so no `format_version` field is added to the replay entry models. Bump the offline report `eval/report_schema.py::CURRENT_FORMAT_VERSION` 1→2 because the `MeetingReport.transcript` shape changed (8.7/8.10); its fail-loud `_validate_format_version` then rejects committed v1 reports, which is why 8.12 regenerates both committed reports + `baseline.json`. Land this before the re-record so the new bytes are stamped consistently.

**Files in scope:**
- eval/report_schema.py (`CURRENT_FORMAT_VERSION` 1→2; the version validator's message; confirm the bump rejects v1)
- orchestrator/replay.py (CONFIRM no `format_version` field is added — document the state_hash + roster.json rationale in a comment/docstring)
- tests/eval/test_report_schema.py (the version-gate tests: v2 is current, v1 rejected with the no-migration message)

**Files NOT in scope:**
- replays/samples/ + the committed reports/baseline regeneration (8.12)
- meetings/, eval metric logic (8.7 / 8.10)

**Definition of done:**
- [ ] `CURRENT_FORMAT_VERSION == 2`; `_validate_format_version` rejects a v1 report fail-loud (no migration), and the version-gate tests assert v2-current / v1-rejected.
- [ ] No `format_version` field is added to the replay entry models; a comment records that the `state_hash` + `roster.json` are the replay-side guard (decision 10).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes (the committed reports are regenerated to v2 in 8.12; until then, any test loading a committed v1 report stays skipped/deferred to 8.12).
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

This is a constant bump + a fail-loud message + a docstring — not a migration. The committed reports become v1-invalid the moment this lands, so 8.12 must regenerate them in the same re-record; any test that loads a committed report stays deferred to 8.12 (note it). Keep the replay entry models field-free for version (the hash already rejects mismatches).

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
Open a PR from branch `phase-8-versioning` with a title like `task 8.11: replay/report versioning`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.4 (versioning); audits/restructure-impact-map-2026-06-04-0223.md §3.3, §5 decision 10), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
