# Agent Prompt — 19.26 Vote-tally parity (consolidation optional)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.26 — Vote-tally parity (consolidation optional), anchored to audits/audit-phase-19-triage.md §7 item 27 [S-Claude; verified in the original triage]; meetings/voting.py:38-48 ("the manager retains its own private copies … future work may consolidate the manager onto this canonical home"); meetings/manager.py:1956-2004 (`_tally` — the implementation the live game applies); the equivalence protected today by prose only. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-vote-tally-parity`
**Depends on:** 19.15
**Section refs:** audits/audit-phase-19-triage.md §7 item 27 [S-Claude; verified in the original triage]; meetings/voting.py:38-48 ("the manager retains its own private copies … future work may consolidate the manager onto this canonical home"); meetings/manager.py:1956-2004 (`_tally` — the implementation the live game applies); the equivalence protected today by prose only
**Complexity:** Medium

The ejection rule the game applies and the one eval re-checks live in two
implementations whose equivalence is protected by a comment. Parity first: a test family
running BOTH implementations over every committed meeting's recorded ballots (all four
sets) plus synthetic edge fixtures (ties, coerced ballots, dead voters, SKIP thresholds,
the guard markers) asserting identical outcomes. THEN, only if parity is total and the
migration is mechanical, consolidate the manager onto `voting.tally_ballots`; otherwise
land the parity suite plus a dated note naming the blocking difference, and the
consolidation goes to the backlog — the fallback is pre-authorized by the triage.

**Files in scope:**
- meetings/manager.py
- meetings/voting.py
- tests/meetings/test_vote_tally_parity.py (new)

**Files NOT in scope:**
- replays/ (evidence, frozen)
- eval/ (consumers of voting.py are untouched)

**Definition of done:**
- [ ] The parity suite covers every committed meeting (count pinned) + the synthetic edges, green on both implementations.
- [ ] Consolidation is either DONE (manager delegates; replay verification + byte-golden green; the private copy gone) or DEFERRED with the blocking difference named in a dated note in voting.py — no third state.
- [ ] `bash scripts/verify_samples.sh` green (reconstruction semantics unchanged).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Drive the committed-meeting sweep from the recorded ballot sets (the meeting records
carry them) rather than re-running meetings; the interesting edges are the ones
production has actually exercised — coerced ballots and redirects are greppable via
their markers. Consolidation, if taken, should leave `_tally` as a thin delegation, not
delete the call site.

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
Open a PR from branch `phase-19-vote-tally-parity` with a title like `task 19.26: vote-tally parity (consolidation optional)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 27 [S-Claude; verified in the original triage]; meetings/voting.py:38-48 ("the manager retains its own private copies … future work may consolidate the manager onto this canonical home"); meetings/manager.py:1956-2004 (`_tally` — the implementation the live game applies); the equivalence protected today by prose only), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
