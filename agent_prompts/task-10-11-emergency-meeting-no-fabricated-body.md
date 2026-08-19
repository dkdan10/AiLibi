# Agent Prompt — 10.11 Emergency-meeting opening: no fabricated body

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.11 — Emergency-meeting opening: no fabricated body, anchored to DESIGN.md §3.2, §5.2, §5.4; audits/audit-2026-06-13-1816-gameplay-data.md B-B-1. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-emergency-no-body`
**Depends on:** 10.10
**Section refs:** DESIGN.md §3.2, §5.2, §5.4; audits/audit-2026-06-13-1816-gameplay-data.md B-B-1
**Complexity:** Medium

All 7 emergency meetings on the close baseline fabricate a found_body on the opening turn:
crewmate_report.v6's emergency variant re-narrates a real-but-stale corpse as a fresh discovery to
justify the suspicion-triggered meeting, and voters anchor ejections on it (seed-27 m1 5/5 cite it,
seed-29 m1 3/6). The 10.8 self-check "no engine body" is TRUE (`body_id` is None) but MASKS the
transcript-level fabrication — it checks the engine field, not the opening turn's observations. Two
loads: (1) `triggering_body_rooms()` reads found_body off turn-0 and now applies a kill-scene Rule-3
exclusion zone to a meeting the design says has no kill scene; (2) the justification chain runs
through a non-existent body. Outcomes were correct, but the basis is fabricated — and it gets worse
under Wave-2 when competent impostors trigger more suspicion meetings.

**Files in scope:**
- agents/strategic/prompts/crewmate_report.j2 (the emergency branch must NOT present a found_body observation — lead with the SUSPICION that crossed 0.60, naming who and the first-hand basis; the body-report branch stays byte-identical; bump crewmate_report v6→v7)
- meetings/transcript.py (`triggering_body_rooms()` gates on the meeting trigger: an emergency meeting returns `frozenset()` regardless of any opening observation, so a fabricated body cannot widen the relevance-gate exclusion zone; thread the trigger_kind in if the transcript does not already carry it — minimal signature extension, one call site)
- orchestrator/game.py (verify the trigger_kind reaches the renderer + the detector path; DEFAULT_PROMPT_VERSIONS crewmate_report v7)
- tests/agents/test_strategic_prompts.py + tests/meetings/test_transcript.py + tests/orchestrator/* + tests/fixtures/prompt_regression/ (regenerate baseline for v7; pins below)

**Files NOT in scope:**
- the emergency TRIGGER / cooldown / eligibility (10.8 — landed and correct; this fixes only the opening's content)
- the body-report opening branch (byte-stable; golden-pinned)
- vote_ballot, the §4.6 render (frozen)
- replays/samples/** (no re-record)

**Definition of done:**
- [ ] The emergency opening renders with NO found_body observation and the called-on-suspicion frame; golden-pin it.
- [ ] The body-report branch renders byte-identically to v6 for body meetings (golden pin both branches); DEFAULT_PROMPT_VERSIONS + version test pins read v7; prompt-regression baseline regenerated.
- [ ] `triggering_body_rooms()` returns `frozenset()` for an emergency meeting even if the opening carries a (fabricated) found_body — unit-pinned; a NEW self-check asserts NO found_body observation on any emergency opening transcript turn (not just `body_id is None`).
- [ ] Offline re-derivation against the committed bytes: confirm the 7 emergency openings' fabricated bodies no longer widen the Rule-3 exclusion zone (the relevance gate result is unchanged or more-correct, never less); no impostor ejection that should have converted is lost.
- [ ] Determinism + the full `bash scripts/check.sh` gate (mypy/ruff/format/lint-imports/generate_prompts --check/validate_task_docs/pytest/frontend) pass.

## Implementation hint

Follow the 10.8 v6 emergency-branch style (it already branches the template on the trigger
substring); this removes the found_body block from that branch rather than adding one. The
`triggering_body_rooms()` gate is the defense-in-depth half — even after the prompt fix, the engine
must not trust an opening's body on an emergency meeting. The new transcript-turn self-check is the
thing the 10.8 check missed; word it to fail loud on any emergency opening with a found_body.

## Public types this task introduces
- `(none)`

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
Open a PR from branch `phase-10-emergency-no-body` with a title like `task 10.11: emergency-meeting opening: no fabricated body`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.2, §5.2, §5.4; audits/audit-2026-06-13-1816-gameplay-data.md B-B-1), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
