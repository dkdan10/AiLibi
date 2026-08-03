# Agent Prompt — 7.10 Fail-soft on malformed meeting statements + single accusation round

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-7.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 7.10 — Fail-soft on malformed meeting statements + single accusation round, anchored to audits/audit-2026-06-01-1425-gameplay-data.md (gp-2, E-E-1, A-A-2, and the R=2 statement-sink in §6); DESIGN.md §5.2 (meeting protocol). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-7.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-7-meeting-failsoft-single-round`
**Depends on:** 7.6 merged
**Section refs:** audits/audit-2026-06-01-1425-gameplay-data.md (gp-2, E-E-1, A-A-2, and the R=2 statement-sink in §6); DESIGN.md §5.2 (meeting protocol)
**Complexity:** Medium

The audit found two independent meeting issues. First (gp-2, blocking): `qwen2.5:7b-instruct` sometimes emits an `AlibiClaim` with `from_tick > to_tick`; the Statement validator rejects it, the meeting aborts, and the game terminates with NO `game_over` record — corrupting 3 of 50 games (seeds 25/36/40) and wasting ~127K input tokens. Second (the owner's speed call): the sequential statement phase runs R=2 rounds — the dominant meeting token sink, roughly a third of meeting LLM calls — the operator's hypothesis is that round 2 is not currently earning its cost, but the audit raised this (E-lens) as an OPEN QUESTION and did not measure a round-2 vote delta — a speed call, not a measured finding; reduce R to 1 for Wave 0.5, readjustable if a Wave-1 measurement later shows round 2 changes outcomes. Both ride the same eval re-record; neither affects replay reconstruction (meetings reconstruct by applying the recorded outcome, so the committed sets are unaffected).

For gp-2 there are two complementary fixes. Parse-tolerance: when an `AlibiClaim` arrives with `from_tick > to_tick`, normalize it (swap the bounds or coerce to a one-tick window at `to_tick`) and retry once — the natural home is 7.6's discriminator-aware normalizer (`llm/report_normalize.py`), extended to the chronological case. Fail-soft: a single rejected `Statement` must degrade to a missed-deadline placeholder (the same default-on-failure mechanism the report/statement collection already uses for timeouts, landed on main as `5407cc7`) so the meeting and game continue to `game_over` — a malformed statement never aborts the run.

R 2→1 is `DEFAULT_ROUND_COUNT` in `meetings/manager.py`; reduce it and update the tests that pin 2 rounds and any round-indexed transcript handling. It is readjustable later if Wave-1 deliberation needs a second round.

**Files in scope:**
- llm/report_normalize.py (extend 7.6's normalizer with the non-chronological-alibi case: swap/coerce `from_tick`/`to_tick`)
- meetings/manager.py (statement collection degrades a rejected `Statement` to a missed-deadline placeholder instead of aborting; `DEFAULT_ROUND_COUNT` 2→1)
- tests/llm/ + tests/meetings/ (a non-chronological alibi normalizes and the meeting reaches `game_over`; a hard-malformed statement fails soft; round count is 1)

**Files NOT in scope:**
- meetings/schemas.py (the `AlibiClaim` chronological validator stays strict — the normalizer fixes the input before validation; the schema is not relaxed)
- engine/, agents/, eval/ (untouched)
- replays/samples/ (no data regeneration here; meetings reconstruct from recorded outcomes, so the committed sets are unaffected by R 2→1)

**Definition of done:**
- [ ] A non-chronological `AlibiClaim` (`from_tick > to_tick`) is normalized (bounds swapped or coerced to a one-tick window) before validation and validates on retry; the strict schema is not relaxed, and a claim still malformed after normalization fails only that single statement, not the run.
- [ ] A single rejected `Statement` degrades to a missed-deadline placeholder and the meeting continues; every game reaches a `game_over` record (no run terminates on a malformed statement). Repro: seed 36 meeting-0 @tick 11 (the recorded `failed_call` with no following `game_over`); also seeds 25 and 40.
- [ ] `DEFAULT_ROUND_COUNT` is 1; the statement phase runs one accusation round; tests pinning 2 rounds and round-indexed handling are updated.
- [ ] The committed 4p/1i and 7p/2i sets still reconstruct byte-identically (meetings apply the recorded outcome; round count does not affect replay) — confirm.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The normalizer (7.6, `llm/report_normalize.py`) already runs in the shared extract→validate path; add a chronological-alibi normalization there so it protects every provider plus the replay path. For fail-soft, reuse the missed-deadline default the sequential report/statement collection already returns on timeout (the `5407cc7` pattern) — catch the `ValidationError` on a single statement and substitute the placeholder rather than propagating. R 2→1 is a one-line constant plus test updates; grep for `round_count` / `DEFAULT_ROUND_COUNT` and round-index assumptions. Reconstruction is unaffected (the loader applies recorded meeting outcomes), so do not touch committed data.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import llm.ollama_client"`

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
Open a PR from branch `phase-7-meeting-failsoft-single-round` with a title like `task 7.10: fail-soft on malformed meeting statements + single accusation round`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-2026-06-01-1425-gameplay-data.md (gp-2, E-E-1, A-A-2, and the R=2 statement-sink in §6); DESIGN.md §5.2 (meeting protocol)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
