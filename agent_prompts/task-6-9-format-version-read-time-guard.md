# Agent Prompt — 6.9 Stricter format-version read-time guarantee

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-6.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 6.9 — Stricter format-version read-time guarantee, anchored to Audit E-E-1; DESIGN.md §11.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-6.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-6-format-version-read-time-guard`
**Depends on:** none
**Section refs:** Audit E-E-1; DESIGN.md §11.3
**Complexity:** Small

`TournamentReport.format_version` has a default of `CURRENT_FORMAT_VERSION`
(`eval/report_schema.py:241`), so a report JSON with the field entirely absent is
silently coerced to v1 and passes, despite the docstring's fail-loud claim — the
`@field_validator` raises only for an explicit out-of-range value (audit E-E-1).
Harmless while v1 is the only format, but it violates the project's
no-silent-fallback discipline: a report that lost its version marker should fail
loud, not default.

Make `format_version` required on the read/deserialization path — remove the
default, or add a `mode="before"` validator that rejects an input dict lacking
the key — so a missing version marker raises a clear error. Keep the existing
out-of-range rejection. This is a small fail-loud hardening; it touches only the
schema and its test.

**Files in scope:**
- eval/report_schema.py
- tests/eval/test_report_schema.py

**Files NOT in scope:**
- api/ (Tasks 6.1/6.5/6.6)
- eval/ (other than report_schema.py)
- orchestrator/replay.py
- replays/samples/ (no fixture change; committed reports already carry the field)

**Definition of done:**
- [ ] Deserializing a report dict that lacks `format_version` raises a clear error (via a required field on the read path or a `mode="before"` validator), rather than silently defaulting to v1 (E-E-1).
- [ ] The existing out-of-range rejection (a value greater than `CURRENT_FORMAT_VERSION` raises) is preserved.
- [ ] In-process construction of a `TournamentReport` continues to work without callers having to pass `format_version` explicitly if the project prefers (e.g. the writer sets it), OR all construction sites are updated — the PR `## Decisions` block states which approach and confirms no writer path regressed.
- [ ] `tests/eval/test_report_schema.py` covers: a dict missing `format_version` is rejected; an out-of-range version is rejected; the current value `1` round-trips.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

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
Open a PR from branch `phase-6-format-version-read-time-guard` with a title like `task 6.9: stricter format-version read-time guarantee`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing Audit E-E-1; DESIGN.md §11.3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
