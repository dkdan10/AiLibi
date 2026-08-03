# Agent Prompt — 8.16 Ballot primary_reason_id integrity

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.16 — Ballot primary_reason_id integrity, anchored to DESIGN.md §5.5; audits/audit-2026-06-06-0632-gameplay-data.md gp-3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-ballot-reason-integrity`
**Depends on:** 8.15
**Section refs:** DESIGN.md §5.5; audits/audit-2026-06-06-0632-gameplay-data.md gp-3
**Complexity:** Medium

Audit gp-3: 24 of 78 non-null ballot `primary_reason_id`s reference turns that do not exist —
voters hallucinate ids or copy the vote prompt's hardcoded example (`m-7:turn-4` appears verbatim in
other meetings' ballots), and a teammate-coerced ballot keeps its stale reason id. This corrupts the
ballot-follows-chain instrument Wave 1 depends on. Validate and normalize at the collection seam,
and make the prompt example real.

**Files in scope:**
- meetings/manager.py (`_collect_one_ballot` validates `primary_reason_id` against the transcript's turn-id set; recoverable `:turn-{k}` suffix forms normalize to the canonical id; unresolvable ids are nulled with an audit marker in `rationale_text` — mirror `_normalize_ballot_target`; `coerce_teammate_ballot_to_skip` additionally nulls the stale reason id)
- agents/strategic/prompts/vote_ballot.j2 (the decision-rule example cites a REAL turn id from the rendered transcript, never a hardcoded one; version marker → `vote_ballot/v4`)
- orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS` vote_ballot → v4)
- tests/meetings/test_manager.py (dangling → nulled + marker; suffix form → canonical; coercion nulls the reason) + tests/agents/test_strategic_prompts.py (the v4 marker; the example sourced from transcript ids)

**Files NOT in scope:**
- meetings/voting.py (tally semantics unchanged — any tally change is a Wave-1 priced decision)
- tests/fixtures/prompt_regression/** + baseline.json (the version bump regenerates them in 8.18, not here)
- replays/samples/**

**Definition of done:**
- [ ] `_collect_one_ballot` accepts canonical turn ids, normalizes recoverable suffix forms, and nulls unresolvable ids with the pinned module-level marker `INVALID_REASON_ID_MARKER: Final[str] = "[invalid primary_reason_id {reason_id!r} nulled] "` prefixed to `rationale_text` (the `INVALID_VOTE_TARGET_MARKER` prefix shape — pin the literal exactly; the 8.18 gate and future audits grep it); `coerce_teammate_ballot_to_skip` nulls `primary_reason_id` on coercion.
- [ ] `vote_ballot.j2` shows a real turn id from the live transcript as its example; the template and `DEFAULT_PROMPT_VERSIONS` read `vote_ballot/v4` in lockstep.
- [ ] The version-pin updates are exhaustive and NO skip-marks are needed: the `assert "vote_ballot/v3" in prompt` case in tests/agents/test_strategic_prompts.py is the only current-code pin (update it to v4); tests/scripts/test_manifest_writer.py's `vote_ballot/v3` assertion and tests/eval/test_prompt_regression.py pin COMMITTED manifest/fixture bytes (still recorded at v3) — leave both untouched; they update/regenerate in 8.18.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The transcript is in scope at ballot collection — build the valid-id set once per vote phase from
`transcript.turns`. A recoverable suffix form is one whose `:turn-{k}` ordinal exists in THIS
meeting (normalize to `{meeting_id}:turn-{k}`); anything else is nulled, never guessed. Use the
pinned `INVALID_REASON_ID_MARKER` literal from the DoD (the `INVALID_VOTE_TARGET_MARKER` prefix
shape, exported alongside it) so downstream eval can count normalizations per game by grepping one
string. The j2 example should reference an id from the transcript the template already iterates, so
it can never dangle.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-8-ballot-reason-integrity` with a title like `task 8.16: ballot primary_reason_id integrity`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.5; audits/audit-2026-06-06-0632-gameplay-data.md gp-3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
