# Agent Prompt — 6.8 Correct README, AGENTS.md, and .env documentation drift

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-6.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 6.8 — Correct README, AGENTS.md, and .env documentation drift, anchored to Audit F-F-1, F-F-2, F-F-3, F-F-5. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-6.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-6-documentation-drift`
**Depends on:** none
**Section refs:** Audit F-F-1, F-F-2, F-F-3, F-F-5
**Complexity:** Small

Several in-repo documentation surfaces have drifted from HEAD (audit Class F).
README attributes "38% impostor win rate, $0.886 total spend" to the bundled
samples (`README.md:89`), but those samples were regenerated 2026-05-27 and now
tally 36% (18/50) and ~$0.91 (MANIFEST sum $0.9075); the 38%/$0.886 figures
describe the original 2026-05-26 closing eval, not the shipped artifacts, and
README's two cost sources disagree (F-F-1). README line 32 says "seven reports
… plus the closing" implying eight, but the glob matches six and the total is
seven (F-F-2). `.env.example:29`'s "API server (Phase 4 — not yet live)" is stale
since the spectator API is live (F-F-3). And `AGENTS.md:47` scopes
`mypy --strict` to engine/observation/agents only, while pyproject sets
`strict=true` globally and `check.sh` runs `mypy .` repo-wide, so an agent could
under-annotate new code (F-F-5).

This task is doc-only and edits only in-repo, agent-editable files. The
auto-memory note drift (F-F-4, the `/eval/tournament-report` route name) was
already corrected on 2026-05-30 and is out of scope (the memory store is outside
the repo). DESIGN.md drift is design-thread-owned and out of scope.

**Files in scope:**
- README.md
- AGENTS.md
- .env.example

**Files NOT in scope:**
- DESIGN.md (design-thread-owned)
- AGENT_IMPLEMENTATION.md
- docs/deployment.md (Task 6.1)
- replays/samples/MANIFEST.md (the canonical provenance record; cite it, do not edit it)
- the auto-memory store (outside the repo; F-F-4 already fixed)

**Definition of done:**
- [ ] `README.md:89` is restated to the actual bundled-sample aggregates — 36% impostor win (18/50) and ~$0.91 per the MANIFEST as the canonical provenance record — OR stops attributing the original 2026-05-26 eval's 38%/$0.886 figures to the regenerated samples; the two disagreeing cost sources are reconciled to MANIFEST (F-F-1).
- [ ] `README.md:32` arithmetic is fixed so "six reports … plus the closing" yields seven, consistent with lines 134/148 (F-F-2).
- [ ] `.env.example:29` drops "— not yet live"; optionally notes `AILIBI_API_PORT` is consumed only by docker-compose (F-F-3).
- [ ] `AGENTS.md:47` states that `mypy --strict` is enforced repo-wide (matching pyproject `strict=true` and `check.sh`'s `mypy .`) (F-F-5).
- [ ] No code or test file is modified; `git diff --name-only` shows only the three doc files.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
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
Open a PR from branch `phase-6-documentation-drift` with a title like `task 6.8: correct readme, agents.md, and .env documentation drift`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing Audit F-F-1, F-F-2, F-F-3, F-F-5), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
