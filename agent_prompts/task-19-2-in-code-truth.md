# Agent Prompt — 19.2 The in-code truth sweep: docstrings match the bytes

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.2 — The in-code truth sweep: docstrings match the bytes, anchored to audits/audit-phase-19-triage.md §7 item 2 [S-Claude; §8 rows 5, 16 — every anchor re-verified at HEAD by the planning session]; agents/memory/beliefs.py:916-928 + :1102-1116 (the false "DEAD in production" pair) vs agents/memory/store.py:455-545 (the live write path, unconditional since 14.9); beliefs.py:1395-1399, :433, :1653, :1689-1692, :1791 (stale default-OFF claims) vs the four resolvers :183-197/:217/:285/:400 (hard-return True); meetings/transcript.py:2386-2387 + :2918-2920 vs resolvers :1360-1409 ("now always True"); meetings/manager.py:301-302, :1900, :1935-1946 (stale "default-OFF" citation-gate claims; the lever is always-ON at meetings/constants.py:54); orchestrator/game.py:12-13 (the false only-importer claim). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-in-code-truth`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-19-triage.md §7 item 2 [S-Claude; §8 rows 5, 16 — every anchor re-verified at HEAD by the planning session]; agents/memory/beliefs.py:916-928 + :1102-1116 (the false "DEAD in production" pair) vs agents/memory/store.py:455-545 (the live write path, unconditional since 14.9); beliefs.py:1395-1399, :433, :1653, :1689-1692, :1791 (stale default-OFF claims) vs the four resolvers :183-197/:217/:285/:400 (hard-return True); meetings/transcript.py:2386-2387 + :2918-2920 vs resolvers :1360-1409 ("now always True"); meetings/manager.py:301-302, :1900, :1935-1946 (stale "default-OFF" citation-gate claims; the lever is always-ON at meetings/constants.py:54); orchestrator/game.py:12-13 (the false only-importer claim)
**Complexity:** Medium

In an agent-built repo, stale prose actively misleads the next agent: an implementer
trusting `beliefs.py`'s docstring would mislabel live production code as dead. Rewrite
every named false docstring to state the current truth, preserving history as history
("graduated at 18.12; was default-OFF") rather than as present tense. Replace
`orchestrator/game.py:12-13`'s false claim with the true, load-bearing invariant
(agents/meetings/llm are engine-free, enforced by import-linter; many privileged modules
import engine). This task executes the sweep; the convention that stops the class
regenerating (rewrite interior docstrings at lever graduation) lands in AGENTS.md via
19.1. Docstring/comment lines only — zero behavior bytes move.

**Files in scope:**
- agents/memory/beliefs.py; (docstring/comment lines only)
- meetings/transcript.py; (same)
- meetings/manager.py; (same)
- orchestrator/game.py; (the :12-13 module-docstring claim only)

**Files NOT in scope:**
- agents/memory/store.py (the live path is evidence, not an edit target)
- meetings/constants.py; (the resolver homes already state "now always True")
- any resolver body or lever mechanism (behavior untouched)

**Definition of done:**
- [ ] Each anchor listed in Section refs now states the truth; a repo grep for the exact stale phrases ("DEAD in production", "default-OFF" on the graduated levers named above) returns zero false claims in the swept files, and the PR quotes the grep.
- [ ] No behavior bytes moved: the diff contains only comment/docstring lines (assert via `git diff` review; the full suite and the prompt byte-golden stay green).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Keep the archaeology — these docstrings carry genuinely valuable history; the fix is tense
and truth, not deletion. Pattern: "LIVE since Task 13.5.2 (write path:
`store.py::record_alibi` from the orchestrator loop). Historical note: declared dead in
the 2026-06-25 diagnosis, revived at 13.5.2." Sweep only the named anchors plus any
same-file instance of the same class you can verify against a resolver in the same
sitting; do not free-hunt across the repo.

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
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
Open a PR from branch `phase-19-in-code-truth` with a title like `task 19.2: the in-code truth sweep: docstrings match the bytes`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 2 [S-Claude; §8 rows 5, 16 — every anchor re-verified at HEAD by the planning session]; agents/memory/beliefs.py:916-928 + :1102-1116 (the false "DEAD in production" pair) vs agents/memory/store.py:455-545 (the live write path, unconditional since 14.9); beliefs.py:1395-1399, :433, :1653, :1689-1692, :1791 (stale default-OFF claims) vs the four resolvers :183-197/:217/:285/:400 (hard-return True); meetings/transcript.py:2386-2387 + :2918-2920 vs resolvers :1360-1409 ("now always True"); meetings/manager.py:301-302, :1900, :1935-1946 (stale "default-OFF" citation-gate claims; the lever is always-ON at meetings/constants.py:54); orchestrator/game.py:12-13 (the false only-importer claim)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
