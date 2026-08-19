# Agent Prompt — 9.8 Suspicion accumulator and decay

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-9.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 9.8 — Suspicion accumulator and decay, anchored to DESIGN.md §6.3 (belief Rules 3 + 5), §4.6; audits/audit-2026-06-09-0347-gameplay-data.md gp-1 (recall). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-9.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-9-suspicion-accumulator`
**Depends on:** 9.7 (shares agents/memory/beliefs.py)
**Section refs:** DESIGN.md §6.3 (belief Rules 3 + 5), §4.6; audits/audit-2026-06-09-0347-gameplay-data.md gp-1 (recall)
**Complexity:** Integration

The first cut of the owner's collective-suspicion model — the recall side of gp-1. 25/47
impostor-accused meetings carry no contradiction (clean fabricated alibi, killed unseen), so no
voter's PRIVATE suspicion reaches 0.60 and the gate forces SKIP. The fix is a decaying accumulator: a
small persistent suspicion bump for being accused in a meeting, plus the deferred decay/clear rules,
so sustained suspicion across rounds converts while one round never does. Accepted to convert weakly
in today's short games (≈1.5 meetings each) — its runway grows once Phase 10 + gp-7 lengthen games.

**Files in scope:**
- agents/memory/beliefs.py (a new accusation-driven rule: an accusation naming a subject adds a SMALL delta, e.g. +0.05, well below the gate alone; wire in the already-present `decay_suspicion` for §6.3 Rule 5 drift toward 0.5 when unreinforced; add Rule 3 corroboration-lowers-suspicion)
- meetings/manager.py + agents/memory/store.py + the game loop (the PERSISTENCE path: the accusation bump must be written to each living agent's PERSISTENT belief state across meetings, unlike the transient vote-time contradiction-lift in `_suspicion_graph_with_contradictions` which rebuilds a throwaway BeliefState — establish/confirm a post-meeting belief-update hook so suspicion carries forward and decays)
- tests/agents/test_beliefs.py + tests/meetings/test_manager.py + tests/agents/test_memory_store.py (one accusation does not cross 0.60; the same subject accused across 2–3 meetings does; an unreinforced bump decays back toward 0.5; a corroboration lowers suspicion; persistence across meetings is asserted)

**Files NOT in scope:**
- the §4.6 gate render in vote_ballot.j2 (FROZEN — this changes how suspicion ACCRUES, not the gate)
- agents/strategic/prompts/** (no prompt edits)
- replays/samples/** (re-record is 9.11)

**Definition of done:**
- [ ] FIRST: the contract verifies/establishes the persistent post-meeting belief-update path; if none exists, building it is part of this task (without persistence the accumulator is inert). The design choice is documented.
- [ ] A single accusation adds the small delta and stays well under 0.60; the same subject accused across 2–3 meetings accumulates over the gate. Pinned numerically.
- [ ] Unreinforced suspicion decays toward 0.5 (Rule 5); a corroboration lowers a subject's suspicion (Rule 3). Both pinned.
- [ ] Determinism + the §1.3 firewall hold: an impostor voter accrues NO accusation-bump against a fellow impostor (the bump rides the same teammate guard as 7.12/9.3); crew leak suites green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The decay half is largely turning on rules already specced in §6.3 and an existing
`beliefs.decay_suspicion`. The hard part is PERSISTENCE: today the contradiction-lift is recomputed
at vote time and thrown away, so a verbal accusation touches nothing durable. Find or add the
post-meeting hook that folds the meeting's accusations into each agent's stored beliefs, then let
decay erode them between meetings. Tune the bump small enough that one round is never decisive — the
owner principle is no single round ejects. If the persistence path must be BUILT rather than found — a
new post-meeting hook + store wiring + determinism + replay-walk safety — expect this task to run
LARGER than 9.7; say so in the PR description so reviewers read the size as scope, not drift.

## Integration risk

The largest Wave-1 task — it changes the cross-meeting belief dynamics shared by all roles. The
teammate-firewall invariant (9.3) and crew byte-identity for non-accusation paths are the hard lines.
Expect muted measured effect in 9.11 (short games); that is known and accepted, not a failure.

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
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-9-suspicion-accumulator` with a title like `task 9.8: suspicion accumulator and decay`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §6.3 (belief Rules 3 + 5), §4.6; audits/audit-2026-06-09-0347-gameplay-data.md gp-1 (recall)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
