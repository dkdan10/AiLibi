# Agent Prompt — 9.1 kill_gifted definition fix + offline report regeneration

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-9.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

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
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-9-kill-gifted-definition` with a title like `task 9.1: kill_gifted definition fix + offline report regeneration`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.5; audits/audit-2026-06-07-0717-gameplay-data.md gp-4 (finding A-A-2)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
