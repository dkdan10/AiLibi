# Agent Prompt — 9.1 kill_gifted definition fix + offline report regeneration

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-9.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 9.1 — kill_gifted definition fix + offline report regeneration, anchored to DESIGN.md §3.5; audits/audit-2026-06-07-0717-gameplay-data.md gp-4 (finding A-A-2). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-9.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-9-kill-gifted-definition`
**Depends on:** none (hygiene root)
**Section refs:** DESIGN.md §3.5; audits/audit-2026-06-07-0717-gameplay-data.md gp-4 (finding A-A-2)
**Complexity:** Small

The committed report undercounts kill-gifted wins (8/46 vs true 11/46): the current flag requires
that NO task instance completed on the final tick, so a same-tick completion by another player
masks a genuine gift (seed 11 tick 20: victim p-6 killed holding upload_logs 4/6 while p-5
completes a different instance the same tick — the win fires on the drop, wrongly excluded).
Re-anchor the definition to the victim: kill-gifted iff the winner is CREWMATES by tasks AND the
final tick resolves a kill whose victim held at least one incomplete instance at kill resolution.
Regenerate both committed reports offline (same bytes, corrected derivation — no re-record).

**Files in scope:**
- eval/balance_eval.py (`_kill_gift_accounting` — the definition swap; aggregates unchanged in shape)
- replays/samples/tournament-eval-report.json + replays/samples/9p2i/tournament-eval-report.json (regenerated OFFLINE from the committed bytes via the build_sample_report path)
- tests/eval/test_balance_eval.py + tests/eval/test_report_schema.py + tests/eval/test_tournament_report.py (the masked-gift fixture: same-tick completion by another player still flags; any `kill_gifted_wins` pin updates — 9p/2i becomes 11)
- tests/api/test_eval.py (only if it pins a kill_gifted aggregate; otherwise untouched)

**Files NOT in scope:**
- eval/report_schema.py field shapes (fields exist from 8.17; values change, schema does not)
- replays/samples/**/*.jsonl + MANIFEST.md (bytes untouched; offline regen only)
- engine/ (the §3.5 drop semantics are unchanged)

**Definition of done:**
- [ ] `kill_gifted` is true iff winner is CREWMATES by tasks AND the final tick resolves a kill whose victim held ≥1 incomplete instance at kill resolution; a same-tick completion by another player does not mask it; derivation stays engine-walk-based (resolved events, not raw action rows).
- [ ] Both committed reports are regenerated offline and `build_sample_report --check` is consistent; the 9p/2i `kill_gifted_wins` reads 11; replay bytes and MANIFESTs are untouched.
- [ ] A regression fixture covers the masked-gift case (kill + unrelated same-tick completion) and the non-gift case (victim held no incomplete instances).
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
Open a PR from branch `phase-9-kill-gifted-definition` with a title like `task 9.1: kill_gifted definition fix + offline report regeneration`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.5; audits/audit-2026-06-07-0717-gameplay-data.md gp-4 (finding A-A-2)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
