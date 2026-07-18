# Agent Prompt — 18.8 The roll-call round (turn-allocation surface, default-OFF)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.8 — The roll-call round (turn-allocation surface, default-OFF), anchored to audits/audit-phase-18-planning.md §3.4 (the 53%-never-speak decomposition; the 2.13× turn-call cost); meetings/manager.py:952-1051 (the three-phase turn allocation), :1940-2010 (`_opt_in_eligible_ids`); audits/audit-phase-17-absence-gate.md Ruling 3(a) (the turn-taking routing this executes). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-roll-call-round`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §3.4 (the 53%-never-speak decomposition; the 2.13× turn-call cost); meetings/manager.py:952-1051 (the three-phase turn allocation), :1940-2010 (`_opt_in_eligible_ids`); audits/audit-phase-17-absence-gate.md Ruling 3(a) (the turn-taking routing this executes)
**Complexity:** Medium

The only surface that can reach the ratified 0.60 crew clause: a flag-gated roll-call round
after the reactive chain — one turn per living player who has not yet spoken, asked for a
structured whereabouts placement (role-blind ask; what impostor templates DO with it is
18.10's separate arm). Default-OFF via an env-gated resolver (the `absence_prior_enabled`
pattern); OFF-path bytes provably identical. Cost honesty in the module docstring: +~3.1
turns/meeting at today's economy (496 → 1057 turn calls over the samples denominator),
~+36% meeting LLM calls — the number the gate and the 18.13 duration plan both quote.

**Files in scope:**
- meetings/manager.py; (the round + the resolver)
- tests/meetings/test_manager.py (OFF-path byte-identity; ON-path allocation fixtures: who is asked, order determinism, living-only, no double-turns)

**Files NOT in scope:**
- meetings/transcript.py; (18.9's region)
- agents/strategic/prompts/; (18.10's region — the round uses the existing role-blind whereabouts ask surface)

**Definition of done:**
- [ ] With the flag OFF (default), committed-bytes reconstruction and all existing meeting fixtures are byte-identical (pinned); with it ON, every living non-speaker receives exactly one roll-call turn in deterministic order after the chain and before ballots, fixture-pinned.
- [ ] The resolver follows the graduated-lever conventions (env override for tests, default-OFF constant, one call site) and the docstring quotes the measured turn-cost arithmetic with its source.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The round slots into `MeetingManager.run` between the chain termination and the ballot
phase; reuse the opt-in turn's prompt surface (the role-blind info-share branch already
asks for a whereabouts observation) so no template work happens here. Deadline handling
mirrors opt-in turns.

## Public types this task introduces
- `meetings.manager.roll_call_round_enabled`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-18-roll-call-round` with a title like `task 18.8: the roll-call round (turn-allocation surface, default-off)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §3.4 (the 53%-never-speak decomposition; the 2.13× turn-call cost); meetings/manager.py:952-1051 (the three-phase turn allocation), :1940-2010 (`_opt_in_eligible_ids`); audits/audit-phase-17-absence-gate.md Ruling 3(a) (the turn-taking routing this executes)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
