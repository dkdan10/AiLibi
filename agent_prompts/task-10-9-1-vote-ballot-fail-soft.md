# Agent Prompt — 10.9.1 Vote-ballot fail-soft

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.9.1 — Vote-ballot fail-soft, anchored to DESIGN.md §5.2, §4.6; PR #147 finding F1 (seed-8 vote-truncation abort). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-vote-ballot-failsoft`
**Depends on:** none (PR #147 F1 repair; all Wave-1 source tasks are merged)
**Section refs:** DESIGN.md §5.2, §4.6; PR #147 finding F1 (seed-8 vote-truncation abort)
**Complexity:** Medium

The first Wave-1 re-record attempt STOPPED on a HARD red: one vote ballot ran to the frozen
1024-token vote cap mid-JSON, the provider-level single retry also failed, the
ValidationError propagated, and the game aborted (game_over 49/50). The asymmetry is the
gap: turns have a fail-soft (7.10 degrades them; 10.6 extended it), ballots do not — the
vote path catches ONLY the deadline (meetings/manager.py:1311-1324 documents malformed
ballots as propagating). A twice-failed ballot must degrade to SKIP with an audit trail, not
kill the game. Caps and retry counts stay FROZEN — this task adds a net, never a retry.

**Files in scope:**
- meetings/manager.py (catch parse/validation failure of a vote-ballot completion AFTER the existing provider-level retry — the same seam where the deadline catch sits; degrade to the existing _default_vote SKIP with a new VOTE_PARSE_DEFAULT_MARKER on rationale_text preserving a BOUNDED head of the unparseable response per the 10.6 60-char rule; record a DefaultedCall with phase vote — follow the 10.6 telemetry precedent: prefer an additive field over a new trigger literal IF a new literal would touch the orchestrator's replay-row writing, verify and document which; the deadline path is byte-unchanged; no new retries, no cap changes)
- eval/vote_correctness.py + eval/meeting_quality.py (extend the standing SKIP partition with a DEFAULTED class keyed on the marker: a degraded SKIP under a MUST-vote render is partitioned like the coerced class — it is NEVER a genuine inversion and never a silent missed skip; report the count beside coerced/missed)
- tests/meetings/test_manager.py + tests/eval/* (pins below)

**Files NOT in scope:**
- the vote/turn token caps and temperatures (frozen), the provider retry count (frozen)
- agents/strategic/prompts/** (no prompt change; the runaway class is accepted at ~1/50 and netted, not prompted away)
- orchestrator/** beyond verifying the abort path is no longer reachable from a malformed ballot (read-verify; if a literal change is forced, stop and surface it in the PR Decisions)
- replays/samples/** (the re-record is 10.9)

**Definition of done:**
- [ ] A ballot completion that fails schema validation twice (synthetic truncated-JSON fixture mirroring the seed-8 shape: response cut mid-string at the cap) degrades to SKIP with VOTE_PARSE_DEFAULT_MARKER, records the DefaultedCall telemetry, and the meeting tallies and the game CONTINUES — integration-pinned at the manager level.
- [ ] The deadline-default path is byte-unchanged (existing pins stay green untouched).
- [ ] Partition pins: a marker-bearing SKIP under a MUST-vote render lands in the DEFAULTED class — threshold_inversions does not move, missed_skip does not move, the defaulted count reads 1; a marker-bearing SKIP under a MUST-skip render is simply correct-skip with telemetry.
- [ ] The marker's quoted head is bounded (unit test with a 3,000-char unparseable blob).
- [ ] Determinism: the degrade is a pure function of the failed response; replaying the same bytes yields the same ballot.
- [ ] `uv run mypy .`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run lint-imports`, `uv run python scripts/generate_prompts.py --check`, `uv run python scripts/validate_task_docs.py`, `uv run pytest`, and `bash scripts/check.sh` all pass.

## Implementation hint

Mirror the deadline catch four lines above the parse site: wrap the model_validate_json in
the same try discipline, reuse _default_vote, and thread the marker through the rationale
the way the teammate-coercion marker does. The 10.6 unsure-degrade decision (additive
DefaultedCall field rather than a new trigger literal, to leave replay-row writing
untouched) is the precedent to follow or consciously diverge from — state which in the PR.

## Public types this task introduces
- `VOTE_PARSE_DEFAULT_MARKER`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-10-vote-ballot-failsoft` with a title like `task 10.9.1: vote-ballot fail-soft`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.2, §4.6; PR #147 finding F1 (seed-8 vote-truncation abort)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
