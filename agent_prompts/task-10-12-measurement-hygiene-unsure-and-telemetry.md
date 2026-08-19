# Agent Prompt — 10.12 Measurement hygiene: unsure-guard + defaulted-ballot telemetry

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.12 — Measurement hygiene: unsure-guard + defaulted-ballot telemetry, anchored to DESIGN.md §5.2, §4.6, §9; audits/audit-2026-06-13-1816-gameplay-data.md H-H-1, H-H-2, H-H-5. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-measurement-hygiene`
**Depends on:** none (file-disjoint from the detector repairs — touches manager.py + orchestrator/eval, dispatchable in parallel)
**Section refs:** DESIGN.md §5.2, §4.6, §9; audits/audit-2026-06-13-1816-gameplay-data.md H-H-1, H-H-2, H-H-5
**Complexity:** Medium

Two measurement blind spots to close before the Wave-2 re-record, so the gate reads true. (1) The
10.3 opening-position guard accepts a 5266-char reasoning-relocation as a deliberate "unsure"
declaration via a bare substring match (`OPENING_UNSURE_MARKER in free_text.lower()`), so the retry
never fires and the meeting collapses to a SKIP husk (seed-30 m1, cost a body-report meeting its
accusation signal). (2) `defaulted_under_must_vote=0` is green BY CONSTRUCTION: a defaulted ballot's
vote call failed and the failed_call record does NOT persist the prompt, so the extractor's §4.6
verdict reconstruction (from successful llm_calls only) always reads `no-render` and routes the
ballot to `skip_unclassified` before the verdict check — seed-8's defaulted ballot was actually a
MUST-VOTE (a firewalled-correct impostor SKIP), invisible to the invariant. A future CREWMATE default
under a real MUST-VOTE would be silently absorbed and mask a missed eject.

**Files in scope:**
- meetings/manager.py (`_opening_takes_position`: gate the unsure declaration on free_text structure — require the position in a SHORT opening (length within a documented bound near the p95 of ~225 chars), OR require non-empty claims/observations when free_text is far above p95, OR route the reasoning-relocation shape (free_text ≫ p95 with empty claims AND empty observations) through the existing 10.3 retry rather than accepting it; do NOT raise the token cap)
- orchestrator/replay.py + orchestrator/game.py (persist the rendered vote PROMPT — or at minimum the rendered §4.6 max/verdict line — onto the failed_call record for a defaulted ballot, so a defaulted ballot's true verdict is classifiable; additive field, replay-row writers updated minimally)
- eval/meeting_quality.py + audits/workflows/extract_gameplay_facts.py (consume the persisted verdict so `defaulted_under_must_vote` can be non-zero; relabel a firewalled impostor MUST-VOTE→SKIP correctly; fix the stale `defaulted_turns.note` that names seeds 8/36/39 — 36/39 have 0 failed_calls)
- tests/meetings/test_manager.py + tests/orchestrator/* + tests/eval/* (pins below)

**Files NOT in scope:**
- the 2048 turn cap / 1024 vote cap (frozen — the fix is the guard + telemetry, never a cap raise)
- the §4.6 render, the retry COUNT (one retry stays one)
- replays/samples/** (no re-record; the persisted-prompt field starts populating at the 10.17 record)

**Definition of done:**
- [ ] Unsure-guard pin: seed-30 m1's 5266-char hollow opening (claims=[] observations=[] containing "unsure") no longer passes `_opening_takes_position`; it routes to the retry or defaults, not a silent valid-unsure; a SHORT genuine "unsure" opening still passes (both pinned).
- [ ] Telemetry pin: a synthetic defaulted ballot whose persisted verdict line reads MUST-VOTE is classified `defaulted_under_must_vote` ≥ 1 (no longer green-by-construction); the seed-8 record is relabelled firewall-correct-SKIP-under-MUST-VOTE; the stale note is corrected/dropped.
- [ ] The persisted-prompt field is additive and the replay reconstructs byte-identically on existing committed bytes (which carry no such field — the reader tolerates its absence).
- [ ] Determinism + full `bash scripts/check.sh` pass.

## Implementation hint

The unsure guard is a few lines at `_opening_takes_position` (manager.py:1898-1924); the structural
test (length/empty-claims-and-observations) is the cheap robust version. The telemetry half is the
more careful one: thread the rendered verdict onto the failed_call at the vote site
(meetings/manager.py vote path → orchestrator replay row), keeping the field optional so committed
single-era bytes still load. The extractor change mirrors the eval one (one-home: consume, don't
re-derive).

## Public types this task introduces
- `(none — an additive failed_call field; name it in the PR)`

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
Open a PR from branch `phase-10-measurement-hygiene` with a title like `task 10.12: measurement hygiene: unsure-guard + defaulted-ballot telemetry`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.2, §4.6, §9; audits/audit-2026-06-13-1816-gameplay-data.md H-H-1, H-H-2, H-H-5), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
