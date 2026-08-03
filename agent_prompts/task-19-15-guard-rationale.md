# Agent Prompt — 19.15 Guard-rationale redaction (the dormant path)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.15 — Guard-rationale redaction (the dormant path), anchored to audits/audit-phase-19-triage.md §7 item 16 [S-Codex; mechanism confirmed by the triage's partner-phrase counts and re-verified at HEAD]; meetings/manager.py:1906-1913 (the call site) + :2893-2925 (`coerce_teammate_ballot_to_skip` — rewrites the target, prepends a marker, and KEEPS `ballot.rationale_text` at :2923, preserving omniscient teammate/self-kill text). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-guard-rationale`
**Depends on:** 19.2
**Section refs:** audits/audit-phase-19-triage.md §7 item 16 [S-Codex; mechanism confirmed by the triage's partner-phrase counts and re-verified at HEAD]; meetings/manager.py:1906-1913 (the call site) + :2893-2925 (`coerce_teammate_ballot_to_skip` — rewrites the target, prepends a marker, and KEEPS `ballot.rationale_text` at :2923, preserving omniscient teammate/self-kill text)
**Complexity:** Small

When the vote guard coerces a teammate ballot to SKIP, the preserved rationale can say
"p-3 is my partner" — spectator-visible omniscience. Replace the preserved rationale with
a neutral strategic reason while KEEPING the audit marker that the guard changed the
target (auditability is never laundered — the redaction is itself marked). Dormant for
committed bytes (they are frozen and unaffected); this matters on any future recording.
Explicitly distinct from model-originated fourth-wall statements, which 19.14 measures
and 19.8 discloses — this fixes only the guard-originated TEXT class. The DISPLAY-side
twin (the `teammate_coerced` chip's perspective gating) is 19.11's; this task never
touches the UI.

**Files in scope:**
- meetings/manager.py; (the guard's rationale construction only)
- tests/meetings/test_vote_guard_rationale.py (new)

**Files NOT in scope:**
- replays/ (committed bytes frozen — the fix is forward-looking)
- meetings/voting.py (19.26's file)

**Definition of done:**
- [ ] A coerced ballot carries the guard marker plus a neutral rationale with zero teammate/self-kill phrasing (fixture-pinned, including the marker's survival for auditability); the docstring labels the path dormant-for-committed-bytes.
- [ ] Committed-byte surfaces are unaffected (full suite + byte-golden green).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

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
Open a PR from branch `phase-19-guard-rationale` with a title like `task 19.15: guard-rationale redaction (the dormant path)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 16 [S-Codex; mechanism confirmed by the triage's partner-phrase counts and re-verified at HEAD]; meetings/manager.py:1906-1913 (the call site) + :2893-2925 (`coerce_teammate_ballot_to_skip` — rewrites the target, prepends a marker, and KEEPS `ballot.rationale_text` at :2923, preserving omniscient teammate/self-kill text)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
