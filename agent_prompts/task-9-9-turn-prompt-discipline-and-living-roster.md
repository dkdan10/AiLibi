# Agent Prompt — 9.9 Turn prompt discipline and living-roster

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-9.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 9.9 — Turn prompt discipline and living-roster, anchored to DESIGN.md §5.1, §5.2, §5.5; audits/audit-2026-06-09-0347-gameplay-data.md gp-3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-9.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-9-turn-prompt-discipline`
**Depends on:** 9.8 (shares meetings/manager.py)
**Section refs:** DESIGN.md §5.1, §5.2, §5.5; audits/audit-2026-06-09-0347-gameplay-data.md gp-3
**Complexity:** Medium

Two 9B-artifact fixes, prompt-layer. (1) Turn-verbosity: with think:false the 9B relocates
deliberation into free_text and overruns the 2048 turn cap, truncating the turn into a fail-soft
default (seeds 8/36/39 — a defaulted opening is a lost chain-driving accusation). Fix it at the
ROOT with a length discipline, NOT by raising the cap (the runaway is unbounded; a higher cap
re-creates the num_ctx overrun the vote rationale hit). (2) Dead-player accusations: the 9B accuses
players no longer living (seeds 11, 33), dropped by the fb3cfa5 validation but wasting the turn —
constrain accusations to the living roster.

**Files in scope:**
- agents/strategic/prompts/crewmate_report.j2 + agents/strategic/prompts/accusation_round.j2 (free_text discipline: "at most 2–3 sentences stating your single conclusion; do NOT narrate or second-guess your reasoning"; a living-roster constraint: "you may ONLY accuse a player on the LIVING list below")
- meetings/manager.py + agents/strategic/prompts/loader.py (thread `living_ids` through `_render_turn_prompt` → `crewmate_report_prompt`/`accusation_round_prompt` → the templates. The accusation roster is living players MINUS the turn's own speaker — an agent cannot accuse itself — mirroring vote_ballot's candidate_targets (living minus voter); reuse the exact filtering, not a parallel implementation)
- orchestrator/game.py (bump DEFAULT_PROMPT_VERSIONS: crewmate_report v3 → v4, accusation_round v5 → v6)
- tests/agents/test_strategic_prompts.py + tests/orchestrator/test_replay_meetings.py (version pins; the living-roster list renders; the discipline text is present; a render-without-living_ids still validates under StrictUndefined per the optional-kwarg pattern)

**Files NOT in scope:**
- meetings/manager.py turn/vote token caps (FROZEN at 2048/1024 — the fix is the prompt, not the cap)
- agents/memory/beliefs.py (no belief change here)
- replays/samples/** (re-record is 9.11)

**Definition of done:**
- [ ] Both turn prompts carry the free_text length discipline; rendered turns state a conclusion without narrating reasoning. The version markers bump (crewmate_report v4, accusation_round v6) end-to-end in a fresh replay entry.
- [ ] The living roster renders into both turn prompts and the templates instruct accusations to stay on it; reuses the candidate_targets threading pattern, not a new one.
- [ ] DEFAULT_PROMPT_VERSIONS + every committed-fresh-replay version assertion updated; committed-fixture assertions (recorded bytes) left UNCHANGED until 9.11 re-records.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The vote ballot already threads candidate_targets (living players minus voter) from the manager into
the prompt; mirror that exact path for the turn prompts' living-roster list rather than inventing a
new channel. The length discipline is the same medicine that fixed the vote rationale (one-sentence
rule) ported to the turn free_text. Do NOT touch the 2048 cap — that is the contract's hard line.

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
Open a PR from branch `phase-9-turn-prompt-discipline` with a title like `task 9.9: turn prompt discipline and living-roster`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.1, §5.2, §5.5; audits/audit-2026-06-09-0347-gameplay-data.md gp-3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
