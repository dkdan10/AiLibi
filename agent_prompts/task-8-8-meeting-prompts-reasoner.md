# Agent Prompt — 8.8 Meeting prompts + reasoner chain producers + version bump

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.8 — Meeting prompts + reasoner chain producers + version bump, anchored to DESIGN.md §4.4 (strategic policy turns), §5.2, §6.6 (prompt rendering); audits/restructure-impact-map-2026-06-04-0223.md §2b, §4 couplings 2 & 4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-meeting-prompts-reasoner`
**Depends on:** 8.7
**Section refs:** DESIGN.md §4.4 (strategic policy turns), §5.2, §6.6 (prompt rendering); audits/restructure-impact-map-2026-06-04-0223.md §2b, §4 couplings 2 & 4
**Complexity:** Integration

Reshape the meeting prompts + the reasoner to produce chain turns against 8.7's schema. The four templates (`accusation_round.j2`, `crewmate_report.j2`, `impostor_report.j2`, `vote_ballot.j2`) become the opening / reactive-turn / opt-in / vote templates; the reasoner's `produce_report` (the opener), `produce_statement` (a chain/opt-in turn — gains a "who accused me / prior turn" input), and `produce_vote` re-sequence; the trigger labels + `_TRIGGER_CALL_KIND` route turns to the meeting tier; the leak-scan allowlist (the impostor's own `fellow_impostor_ids`) carries over. Bump the four prompt versions in lockstep (they all land in `MeetingReplayEntry.prompt_versions`) and `orchestrator/game.py::DEFAULT_PROMPT_VERSIONS` + `DefaultMeetingRunner`/`build_default_meeting_runner`. `impostor_report.j2` + `vote_ballot.j2` carry the 7.12 firewall block. Editing `Statement` (8.7) changes the LLM `format=` schema — the provider tests are 8.9.

**Files in scope:**
- agents/strategic/prompts/accusation_round.j2 + crewmate_report.j2 + impostor_report.j2 + vote_ballot.j2 (reshaped to opening / reactive-turn / opt-in / vote; the four versions bump in lockstep; 7.12 blocks preserved)
- agents/strategic/prompts/loader.py (the opening / turn / opt-in / vote loaders + the reactive-turn input; `StrictUndefined` fails loud on a missing kwarg)
- agents/strategic/reasoner.py (`produce_report`/`produce_statement`/`produce_vote` + trigger allow-lists + `_TRIGGER_CALL_KIND`; the leak-scan + 7.12 guards on every turn)
- orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS` bumped; `DefaultMeetingRunner` / `build_default_meeting_runner` wire the reshaped callables; the prompt imports)
- tests/agents/test_strategic_prompts.py + test_strategic_reasoner.py (render each reshaped template + the new version markers; the three producers + the 7.12 guard on the chain path)

**Files NOT in scope:**
- meetings/ (the protocol + schema are 8.7)
- tests/llm/ (the provider parse-tolerance is 8.9)
- eval/, api/, frontend/ (8.10)

**Definition of done:**
- [ ] The four meeting templates render the chain shapes (opening / reactive turn with the prior-turn input / opt-in / vote); a crewmate's prompts carry no teammate block; an impostor's carry the 7.12 firewall block.
- [ ] `reasoner.py` produces an opening `MeetingTurn`, a chain/opt-in `MeetingTurn` (with `reply_to`), and a `VoteBallot`; the deterministic teammate guard + the leak scan run on every turn; the trigger labels route to the meeting tier with correct cost attribution.
- [ ] The four prompt versions bump in lockstep and are recorded via `DEFAULT_PROMPT_VERSIONS` / `MeetingReplayEntry.prompt_versions`; `tests/agents/test_strategic_prompts.py` pins the new markers.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The reasoner already branches the opener on role and runs the 7.12 guard + leak scan per output — extend those to every chain/opt-in turn and feed the reactive-turn template the accusing turn. Bump all four template version headers AND `DEFAULT_PROMPT_VERSIONS` together (a stale marker fails the manifest/replay cross-check). Keep the leak-scan allowlist for an impostor's own `fellow_impostor_ids` (the `## Your role:` precedent). No metric/api change here (8.10).

## Integration risk

The four-template version bump is atomic — a partial bump fails the replay/manifest provenance cross-check. The 7.12 firewall must hold on every turn-kind (not just the old statement slot). The `Statement`→`MeetingTurn` schema edit changes the JSON the provider is constrained by, so 8.9 must land with/after this.

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
Open a PR from branch `phase-8-meeting-prompts-reasoner` with a title like `task 8.8: meeting prompts + reasoner chain producers + version bump`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §4.4 (strategic policy turns), §5.2, §6.6 (prompt rendering); audits/restructure-impact-map-2026-06-04-0223.md §2b, §4 couplings 2 & 4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
