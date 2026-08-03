# Agent Prompt — 10.3 Prompt nudges

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.3 — Prompt nudges, anchored to DESIGN.md §5.1, §5.2; audits/audit-2026-06-10-1820-gameplay-data.md gp-9 (H-H-1, H-H-2, H-H-3, D-D-8). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-prompt-nudges`
**Depends on:** 10.2 (shares meetings/manager.py)
**Section refs:** DESIGN.md §5.1, §5.2; audits/audit-2026-06-10-1820-gameplay-data.md gp-9 (H-H-1, H-H-2, H-H-3, D-D-8)
**Complexity:** Medium

Three residual 9B artifacts, prompt-and-validation layer (the 2048 cap stays frozen; the roster
render is byte-verified correct, so these are model-side mitigations): (1) five openings
narrated without making any accusation claim, killing the chain on turn 0 (seeds 23, 39, 44, 13
m0, 38 m1 — distinct from the 2 cap-defaults); (2) the remaining defaults are structured-array
repetition loops (a sighting repeated ~5x until the cap), no longer prose relocation; (3) id
hallucination shifted shape — 17/18 invalid targets are now DEAD real players (12 impostor-
spoken), not invented ids, and the living-roster block does not say who is dead.

**Files in scope:**
- meetings/manager.py (opening validation: an opening turn whose claims carry neither an accusation nor an explicit unsure marker triggers the existing parse-retry path once before fail-soft — reuse the retry machinery, no new channel)
- agents/strategic/prompts/crewmate_report.j2 + agents/strategic/prompts/impostor_report.j2 (openings: require an accusation claim OR an explicit "unsure" statement in free_text; add the anti-repetition line "list each sighting once"; render the DEAD players as an explicit do-not-accuse line under the living roster)
- agents/strategic/prompts/accusation_round.j2 (anti-repetition line + the DEAD line; reply/opt-in unchanged otherwise)
- orchestrator/game.py (DEFAULT_PROMPT_VERSIONS bumps: crewmate_report v4 -> v5, impostor_report v3 -> v4, accusation_round v6 -> v7)
- tests/agents/test_strategic_prompts.py + tests/meetings/test_manager.py + tests/orchestrator/test_replay_meetings.py (version pins on fresh replays; the opening-retry shape; DEAD-line renders; committed-fixture pins left for 10.5)

**Files NOT in scope:**
- meetings/manager.py turn/vote token caps (FROZEN at 2048/1024)
- agents/strategic/prompts/vote_ballot.j2 (the §4.6 render is FROZEN)
- meetings/schemas.py (no MeetingTurn shape change — the unsure marker is free_text-level, validated manager-side)
- replays/samples/** (re-record is 10.5)

**Definition of done:**
- [ ] A narration-only opening (no accusation claim, no unsure marker) triggers exactly one retry through the existing parse-retry path, then fail-softs as today — pinned with a stub that returns narration-only once then a valid opening.
- [ ] Both opening templates instruct accuse-or-declare-unsure; all three turn templates carry the list-each-sighting-once line; the roster block renders DEAD players explicitly as non-targets. Render tests pin each.
- [ ] Version markers bump end-to-end (crewmate_report.v5, impostor_report_v4, accusation_round.v7) in a fresh replay entry; committed-byte fixture pins untouched until 10.5.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The opening-retry reuses the machinery 7.10/8.9 built — wire the validation into the existing
single-retry path rather than inventing a second loop. The DEAD line is the negative list the
model is missing: 17/18 hallucinations were dead-real ids, so naming the dead explicitly attacks
the observed failure, not a guessed one. Keep all three nudges terse — the free_text discipline
medians (~230 chars) prove the model follows short imperatives.

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
Open a PR from branch `phase-10-prompt-nudges` with a title like `task 10.3: prompt nudges`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.1, §5.2; audits/audit-2026-06-10-1820-gameplay-data.md gp-9 (H-H-1, H-H-2, H-H-3, D-D-8)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
