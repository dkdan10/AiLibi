# Agent Prompt — 10.7 Testimony ingestion (pre-vote, two-witness)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.7 — Testimony ingestion (pre-vote, two-witness), anchored to DESIGN.md §5.2, §6.3, §4.6; audits/audit-2026-06-11-2218-gameplay-data.md gp-2 (C-C-1, C-C-2, C-C-3, D-D-3, C-C-6); the corroborate-within-round owner principle. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-testimony-ingestion`
**Depends on:** 10.6
**Section refs:** DESIGN.md §5.2, §6.3, §4.6; audits/audit-2026-06-11-2218-gameplay-data.md gp-2 (C-C-1, C-C-2, C-C-3, D-D-3, C-C-6); the corroborate-within-round owner principle
**Complexity:** Integration

The b1 lever. Spoken testimony currently never enters listeners' beliefs: 38/53 testimony
pairs already had an over-gate eyewitness and 30/53 had witness ballot follow-through, yet
47/50 such meetings SKIPPED because listeners parked at 0.58 and the SKIP bloc won. This task
folds qualifying testimony into every living listener's PERSISTENT belief BEFORE ballots, so
an eyewitness can recruit a plurality within the round — under the independence gate that
keeps bare verbal pile-ons powerless.

**Files in scope:**
- meetings/transcript.py (a pure helper deriving the INDEPENDENT VOICES for each accused subject from the transcript: a voice is a chain/opening turn accusing the subject that carries at least one first-hand observation claim about the subject which passes the 10.6 relevance predicate, or an opt-in corroboration supporting an accuser of the subject that itself carries such an observation; voices must be distinct speakers, never the subject; bare verbal accusations carry no voice)
- agents/memory/beliefs.py (the two-witness rule: subjects with 2+ independent voices take the +0.05 accused-bump PRE-VOTE, applied to every living listener, deduped once per meeting per subject, written to the persistent store; subjects below the bar keep today's post-vote path; the pre-vote fold REPLACES the post-vote accused-bump for that subject-meeting — a folded subject is marked so the post-vote half skips it; the impostor teammate guard applies to this channel)
- meetings/manager.py (restructure the meeting fold into two deterministic halves that ALWAYS run: pre-vote half = two-witness testimony bumps + this meeting's relevance-gated corroborations, both directions symmetric; post-vote half = single-voice accused-bumps + Rule-5 decay, exactly as today; vote prompts render AFTER the pre-vote half so the §4.6 verdict reads post-fold values — the gate computation itself is untouched)
- tests/meetings/test_transcript.py + tests/agents/test_beliefs.py + tests/meetings/test_manager.py

**Files NOT in scope:**
- agents/strategic/prompts/** (the §4.6 render and all templates frozen; no prompt knows about the fold — listeners see updated numbers, nothing else)
- eval/** (10.6 shipped the gauges; this task changes no metric)
- the 9.8 constants (the +0.05 unit is reused, not re-tuned; decay untouched)
- engine/**, orchestrator/** (meeting-layer only)
- tests/fixtures/prompt_regression/** (10.8 owns the v6 baseline regeneration; this task changes no template, and the regression fixture renders from fixed inputs unaffected by fold timing)
- replays/samples/**

**Definition of done:**
- [ ] Single-voice regression: a meeting with one accuser (or any number of bare verbal accusers) produces a persistent post-meeting state byte-identical to pre-change behavior — the channel is invisible until independence is met.
- [ ] Two-voice fold: two observation-backed accusers (or one plus a qualifying opt-in corroboration) move every living listener's view of the subject by exactly +0.05 pre-vote, once, persisted; the post-vote half demonstrably skips the accused-bump for that subject (the double-fold test is mandatory — the per-meeting total for a folded subject equals the unfolded total).
- [ ] Pile-on pin (the owner-principle tripwire): replaying the rule offline over seed 30 m1 produces NO pre-vote fold for p-7 (3 accusers, none with qualifying observation backing). If the implementation finds a qualifying second voice there, STOP and escalate — do not ship a rule that converts that meeting.
- [ ] Yield pins: the offline replay reproduces the audit's two-witness simulation rows — seeds 2 m1 and 5 m1 each lift at least one additional listener to 0.60 or above pre-vote.
- [ ] Same-phase symmetry: a relevance-gated corroboration in the same meeting folds pre-vote alongside the bumps (a defended subject is cleared before ballots, not a meeting late — the seed-28 shape).
- [ ] Render-after-fold consistency: when a listener's view of a folded subject crosses 0.60 pre-vote, the rendered vote prompt shows the post-fold value AND the in-prompt §4.6 verdict reads MUST vote for that listener — graph and verdict computed from ONE post-fold state source; a stale pre-fold graph anywhere in the render path is the bug this pin catches. Unit-pinned: render a vote prompt after a two-voice fold and assert both the value and the verdict line. (A model skip against a freshly-folded MUST-vote render would be a NEW inversion class; 10.9's 0-inversion line plus its fold-crossed spot-walk cover the recorded side.)
- [ ] Teammate guard holds on the new channel; rendered values stay on the quantized lattice; determinism (same transcript, byte-identical fold).
- [ ] `uv run mypy .`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run lint-imports`, `uv run python scripts/generate_prompts.py --check`, `uv run python scripts/validate_task_docs.py`, `uv run pytest`, and `bash scripts/check.sh` all pass.

## Implementation hint

Split the existing fold by moving invocation points, not duplicating logic — one fold
function with a phase argument, called twice per meeting. The voices helper is pure and lives
beside the classifier; it reuses the 10.6 relevance predicate verbatim (one home). The
audit's §4.2 simulation is the executable spec for the yield pins; its per-voter rendered
graphs are in the audit facts. Mark folded subjects on the meeting context, not in the
belief store (the store should never know about phases).

## Integration risk

Cascade is the risk this design exists to prevent; the three guards are observation backing,
the relevance predicate, and the two-voice bar — the seed-30 STOP pin is the tripwire wired
to the owner principle. The double-fold hazard is the one bug class that silently doubles
the constant; its test is non-negotiable. Vote prompts now render mid-meeting-updated
values: the §4.6 inversion count must stay 0 on the 10.9 re-record (gate stacks).

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
Open a PR from branch `phase-10-testimony-ingestion` with a title like `task 10.7: testimony ingestion (pre-vote, two-witness)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.2, §6.3, §4.6; audits/audit-2026-06-11-2218-gameplay-data.md gp-2 (C-C-1, C-C-2, C-C-3, D-D-3, C-C-6); the corroborate-within-round owner principle), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
