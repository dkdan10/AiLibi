# Agent Prompt — 10.9.2 Ballot-target graph guard

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.9.2 — Ballot-target graph guard, anchored to DESIGN.md §4.6, §6.3; PR #147 finding F2 (seed-12 m0 unattributed ejection); the fb3cfa5 layered-guard pattern. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-ballot-target-guard`
**Depends on:** 10.9.1
**Section refs:** DESIGN.md §4.6, §6.3; PR #147 finding F2 (seed-12 m0 unattributed ejection); the fb3cfa5 layered-guard pattern
**Complexity:** Medium

The last unguarded seam for a RANDOM ejection: a voter whose §4.6 verdict reads MUST-vote
may name ANY living candidate as target — including one their own rendered graph carries no
over-gate row for (seed 12 m0: three voters MUST-vote off p-6 at 0.80, adopted the
opening's bare verbal accusation of p-1 instead, p-1 ejected 3-2-2 with zero design-channel
attribution). Every existing guard held; the leak is that ballot TARGET is unconstrained by
the graph the verdict was computed from. Add the deterministic guard at the existing
normalization chokepoint: an eject ballot under a MUST-vote verdict must name a target
whose rendered suspicion meets the threshold; otherwise redirect to the highest-rendered
eligible candidate with an audit marker. The owner principle this enforces is the phase's
oldest line: innocents are ejectable, never at RANDOM.

**Files in scope:**
- meetings/manager.py (extend the _normalize_ballot_target chain — AFTER roster normalization and the 7.12 teammate coercion: when the verdict over candidate_targets reads MUST-vote (max rendered suspicion at or above skip_confidence_threshold, computed from the SAME suspicion_graph and candidate_targets passed to the prompt renderer) and the ballot names an eject target whose rendered row is below threshold or absent, redirect the target to the argmax-rendered candidate in the eligible pool — candidate_targets minus the voter minus fellow_impostor_ids — with ties broken by lowest player id; if the eligible pool's max is below threshold (an impostor voter whose only over-gate row is a teammate), coerce to SKIP instead; either way mark rationale_text with BALLOT_TARGET_REDIRECT_MARKER preserving the original target, bounded per the 10.6 rule. The guard NEVER fires on SKIP ballots, never on MUST-skip verdicts — a vote against a MUST-skip verdict stays a recorded inversion, frozen measurement semantics)
- eval/vote_correctness.py + eval/meeting_quality.py (the gp-7 channel decomposition and the graph-consistency census read the REDIRECTED target; the redirect marker count publishes beside the invalid-target and coercion counts; unattributed impostor ejections must be structurally impossible on post-guard recordings)
- tests/meetings/test_manager.py + tests/eval/* (pins below)

**Files NOT in scope:**
- the §4.6 threshold/render and the tally (frozen — this guard constrains the TARGET of an eject ballot, never the eject-vs-skip choice and never the plurality rule)
- agents/strategic/prompts/** (no prompt change; the model keeps free choice among over-gate targets)
- agents/memory/beliefs.py, meetings/transcript.py (the graph is consumed, not changed)
- replays/samples/**

**Definition of done:**
- [ ] Seed-12 byte pin (from the PR #147 evidence branch fixture, reproduced synthetically if the branch is pruned): given m0's recorded graphs and ballots, the guard redirects the three no-row p-1 ballots to p-6 (the 0.80 argmax) with markers; the two over-gate-consistent ballots are untouched.
- [ ] Over-gate freedom: a ballot naming ANY target whose row meets the threshold passes unredirected even when a higher row exists (no argmax-only over-constraint).
- [ ] Firewall composition: an impostor voter is never redirected to a fellow impostor; the teammate-only-over-gate case coerces to SKIP with the marker; betrayal stays 0 by construction.
- [ ] Frozen-semantics regression: MUST-skip-verdict ballots and SKIP ballots are byte-unchanged through the guard; threshold_inversions and missed_skip move by exactly 0 on a no-redirect transcript.
- [ ] Verdict-equality cross-check: the guard's MUST-vote derivation equals the rendered in-prompt verdict on the same inputs (parse the rendered line in-test via the eval suspicion-parse helper).
- [ ] Determinism: same graph + ballot yields the same redirect; tie-break pinned.
- [ ] `uv run mypy .`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run lint-imports`, `uv run python scripts/generate_prompts.py --check`, `uv run python scripts/validate_task_docs.py`, `uv run pytest`, and `bash scripts/check.sh` all pass.

## Implementation hint

The chokepoint already has every input in scope at the call site (suspicion_graph,
candidate_targets, skip_confidence_threshold, fellow_impostor_ids — manager.py:1292-1295).
Order matters and is pinned: roster normalization, then teammate coercion, then this guard
— so the guard only ever sees valid living non-teammate targets and cannot create a
betrayal ballot for the firewall to re-coerce. Reuse the marker construction discipline
from the teammate-coercion marker.

## Public types this task introduces
- `BALLOT_TARGET_REDIRECT_MARKER`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-10-ballot-target-guard` with a title like `task 10.9.2: ballot-target graph guard`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §4.6, §6.3; PR #147 finding F2 (seed-12 m0 unattributed ejection); the fb3cfa5 layered-guard pattern), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
